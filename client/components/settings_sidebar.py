# Component: LLM settings in the sidebar (model, temperature, max tokens).
# Drawn once in app.py, so it's visible on every page and keeps its values
# when you switch pages. Returns {"model", "temperature", "max_tokens"}.

import streamlit as st


def settings_sidebar(models, defaults):
    # models:   {model_id: {"label", "temperature"}}, from api_client.get_models()
    # defaults: {"model", "temperature", "max_tokens"}, from api_client.get_default_settings()
    model_ids = list(models)

    with st.sidebar:
        st.markdown("### ⚙️ LLM settings")

        model = st.selectbox(
            "Model",
            model_ids,
            index=model_ids.index(defaults["model"]),
            format_func=lambda model_id: models[model_id]["label"],  # show the label, not the id
            help="Prices in USD per 1M input / output tokens.",
            key="setting_model",
        )

        supports_temperature = models[model]["temperature"]
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=defaults["temperature"],
            step=0.1,
            disabled=not supports_temperature,
            help="Low = focused and repeatable, high = more varied and creative.",
            key="setting_temperature",
        )
        if not supports_temperature:
            st.caption("This model ignores temperature (reasoning model).")

        max_tokens = st.number_input(
            "Max tokens",
            min_value=100,
            max_value=16000,
            value=defaults["max_tokens"],
            step=500,
            help="Upper limit for the reply. GPT-5 models also count their hidden "
            "thinking here, so very low values cut the reply off.",
            key="setting_max_tokens",
        )

    return {"model": model, "temperature": temperature, "max_tokens": int(max_tokens)}
