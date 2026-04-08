from fastapi.testclient import TestClient
import pytest

from app.main import app


client = TestClient(app)


def test_optimize_preserves_structured_requirements() -> None:
    prompt = """SYSTEM INSTRUCTIONS AND DETAILED REQUEST:
Hello there, Assistant. I am looking for some very high-quality help today regarding a complex topic. I would like for you to please take a moment to look over the following information very carefully before you start to generate a response for me.

The task at hand is that I need a comprehensive, highly detailed, and very thorough executive summary of the impact of artificial intelligence on the global renewable energy sector. I am specifically interested in how AI can help with things like solar panel efficiency and wind turbine maintenance, but also how it might be used to optimize the power grid itself in real-time.

Please keep in mind that I need this summary to be professional in tone. Do not include any unnecessary filler words. It is very important that you focus on the most important aspects and leave out the minor details that don't matter as much. I want the final output to be concise but still cover all the main points I mentioned above.

In addition to that, could you also please make sure that you provide three specific examples of companies that are currently doing work in this space? It would be great if you could list them in a bulleted list format so it's easy for me to read.

To recap:
1. Give me an executive summary of AI in renewable energy.
2. Focus on solar, wind, and grid optimization.
3. Keep the tone professional and concise.
4. Provide three examples of companies.
5. Make sure you don't repeat yourself or use too many words.
"""

    response = client.post(
        "/optimize",
        headers={"X-API-Key": "dev-key-123"},
        json={"prompt": prompt, "mode": "eco"},
    )

    assert response.status_code == 200
    data = response.json()
    optimized = data["optimized_prompt"].lower()

    assert "executive summary" in optimized
    assert "solar" in optimized
    assert "wind" in optimized
    assert "grid" in optimized
    assert "three" in optimized or "3" in optimized

    # Ensure eco mode reduces, but does not destroy structure/intent.
    assert data["tokens_after"] > 0
    assert data["token_reduction_pct"] < 85


def test_modes_have_distinct_reduction_profiles() -> None:
    prompt = """SYSTEM INSTRUCTIONS AND DETAILED REQUEST:
Hello there, Assistant. I am looking for some very high-quality help today regarding a complex topic.

The task at hand is that I need a comprehensive, highly detailed, and very thorough executive summary of the impact of artificial intelligence on the global renewable energy sector.

Please keep in mind that I need this summary to be professional in tone. Do not include any unnecessary filler words.

In addition to that, please provide three specific examples of companies that are currently doing work in this space.

To recap:
1. Give me an executive summary of AI in renewable energy.
2. Focus on solar, wind, and grid optimization.
3. Keep the tone professional and concise.
4. Provide three examples of companies.
5. Make sure you don't repeat yourself or use too many words.

Thank you very much for your help with this task.
"""

    def call(mode: str) -> dict:
        response = client.post(
            "/optimize",
            headers={"X-API-Key": "dev-key-123"},
            json={"prompt": prompt, "mode": mode},
        )
        assert response.status_code == 200
        return response.json()

    eco = call("eco")
    balanced = call("balanced")
    high_quality = call("high_quality")

    assert eco["token_reduction_pct"] >= balanced["token_reduction_pct"]
    assert balanced["token_reduction_pct"] >= high_quality["token_reduction_pct"]

    # The reductions should be meaningfully different for structured prompts.
    assert eco["token_reduction_pct"] >= 8
    assert balanced["token_reduction_pct"] >= 3


@pytest.mark.parametrize(
    "prompt,required_terms",
    [
        (
            """SYSTEM INSTRUCTIONS:
Please produce an executive summary on AI in renewable energy.
Focus on solar forecasting, wind maintenance, and grid optimization.
Keep a professional concise tone.
Provide three company examples.
To recap:
1. Executive summary.
2. Solar, wind, grid.
3. Professional concise tone.
4. Three companies.
""",
            ["executive summary", "solar", "wind", "grid", "three"],
        ),
        (
            """I need a detailed but concise explanation of how AI improves renewable systems.
Discuss predictive maintenance for wind turbines, performance tuning for solar assets,
and real-time balancing for electric grids. Keep it professional and avoid filler.
Include three examples of companies deploying these systems in production.""",
            ["wind", "solar", "grids", "companies"],
        ),
        (
            """Need an executive summary for AI in renewable energy.
Need an executive summary for AI in renewable energy.
Need an executive summary for AI in renewable energy.
Focus on solar and wind.
Focus on solar and wind.
Include three companies and keep it concise.
Include three companies and keep it concise.
""",
            ["executive summary", "solar", "wind", "companies"],
        ),
    ],
)
def test_all_modes_across_prompt_patterns(prompt: str, required_terms: list[str]) -> None:
    def call(mode: str) -> dict:
        response = client.post(
            "/optimize",
            headers={"X-API-Key": "dev-key-123"},
            json={"prompt": prompt, "mode": mode},
        )
        assert response.status_code == 200
        return response.json()

    eco = call("eco")
    balanced = call("balanced")
    high_quality = call("high_quality")

    # Mode ordering: eco should be most aggressive, high_quality least aggressive.
    assert eco["tokens_after"] <= balanced["tokens_after"]
    assert balanced["tokens_after"] <= high_quality["tokens_after"]

    assert eco["token_reduction_pct"] >= balanced["token_reduction_pct"]
    assert balanced["token_reduction_pct"] >= high_quality["token_reduction_pct"]

    high_text = high_quality["optimized_prompt"].lower()
    for term in required_terms:
        assert term in high_text


def test_high_quality_retains_more_context_than_balanced() -> None:
    prompt = """SYSTEM INSTRUCTIONS AND DETAILED REQUEST:
Hello there, Assistant. I am looking for very high-quality help.
Please read carefully.

I need a comprehensive executive summary of AI in renewable energy.
Focus on solar panel efficiency, wind turbine maintenance, and real-time grid optimization.
Keep the tone professional and concise.
Provide three specific company examples.

To recap:
1. Executive summary.
2. Focus on solar, wind, grid.
3. Professional concise tone.
4. Three companies.
"""

    balanced = client.post(
        "/optimize",
        headers={"X-API-Key": "dev-key-123"},
        json={"prompt": prompt, "mode": "balanced"},
    ).json()
    high_quality = client.post(
        "/optimize",
        headers={"X-API-Key": "dev-key-123"},
        json={"prompt": prompt, "mode": "high_quality"},
    ).json()

    assert high_quality["tokens_after"] >= balanced["tokens_after"]
    assert high_quality["token_reduction_pct"] <= balanced["token_reduction_pct"]


def test_mode_aware_deduplication_preserves_more_in_high_quality() -> None:
    prompt = """Need an executive summary for AI in renewable energy.
Focus on solar and wind.
Need an executive summary for AI in renewable energy.
Include three companies and keep it concise.
Need an executive summary for AI in renewable energy.
"""

    eco = client.post(
        "/optimize",
        headers={"X-API-Key": "dev-key-123"},
        json={"prompt": prompt, "mode": "eco"},
    ).json()
    balanced = client.post(
        "/optimize",
        headers={"X-API-Key": "dev-key-123"},
        json={"prompt": prompt, "mode": "balanced"},
    ).json()
    high_quality = client.post(
        "/optimize",
        headers={"X-API-Key": "dev-key-123"},
        json={"prompt": prompt, "mode": "high_quality"},
    ).json()

    assert eco["tokens_after"] <= balanced["tokens_after"]
    assert balanced["tokens_after"] <= high_quality["tokens_after"]


def test_all_modes_preserve_core_intent_terms() -> None:
    prompt = """SYSTEM INSTRUCTIONS AND DETAILED REQUEST:
I need an executive summary of AI in renewable energy.
Focus on solar panel efficiency, wind maintenance, and real-time grid optimization.
Keep the response professional and concise.
Provide three specific company examples.
Do not add filler content.
"""

    required_terms = [
        "executive",
        "summary",
        "solar",
        "wind",
        "grid",
        "professional",
        "concise",
        "company",
    ]

    for mode in ("eco", "balanced", "high_quality"):
        response = client.post(
            "/optimize",
            headers={"X-API-Key": "dev-key-123"},
            json={"prompt": prompt, "mode": mode},
        )
        assert response.status_code == 200
        data = response.json()
        text = data["optimized_prompt"].lower()

        # No mode should lose core user intent.
        for term in required_terms:
            assert term in text


def test_high_quality_is_context_first_not_size_first() -> None:
    prompt = """Hello assistant, please read carefully.
I need a comprehensive and detailed executive summary on AI for renewable energy operations.
Cover solar diagnostics, wind turbine predictive maintenance, and smart-grid balancing.
Use a professional concise tone and include three company examples.
Thank you very much.
"""

    response = client.post(
        "/optimize",
        headers={"X-API-Key": "dev-key-123"},
        json={"prompt": prompt, "mode": "high_quality"},
    )
    assert response.status_code == 200
    data = response.json()

    # In high_quality mode, aggressive reduction should not happen.
    assert data["token_reduction_pct"] <= 35
