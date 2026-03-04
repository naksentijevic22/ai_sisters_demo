import streamlit as st
from agent.graph import agent

st.set_page_config(page_title="Chez Madeleine", page_icon="🥐", layout="centered")

st.title("🥐 Chez Madeleine — Assistant Boulangerie")
st.caption("Bonjour Madeleine ! Je suis là pour vous aider à gérer votre boulangerie.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Posez votre question à l'assistant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Je réfléchis..."):
            response = agent.invoke({
                "messages": [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            })
            answer = response["messages"][-1].content

        st.markdown(answer)

        # Show tool calls in expander
        tool_calls = [
            m for m in response["messages"]
            if hasattr(m, "type") and m.type == "tool"
        ]
        if tool_calls:
            with st.expander("🔧 Outils utilisés"):
                for tc in tool_calls:
                    st.code(tc.content[:500], language="text")

    st.session_state.messages.append({"role": "assistant", "content": answer})
