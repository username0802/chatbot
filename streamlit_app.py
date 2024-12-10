import streamlit as st
from openai import OpenAI

# Initialize the chat list in session state
if "chat_list" not in st.session_state:
    st.session_state.chat_list = ['main']
    st.session_state.chat_list_option = {'main' : {'language':'', 'level':'', 'topic':''}}

# Side panel for chat selection and options
with st.sidebar:
    st.header("Your Chatting")
    selected_chat = st.radio(
        "Select a chat about",
        st.session_state.chat_list,
        #format_func=lambda x: x.capitalize(),
        #index=2  # Assuming new_chat3 should be the default selection
    )

    st.header("Create new")
    language = st.selectbox('Select language', ['English', 'korean', 'japanese'])
    level = st.selectbox('Your level', ['beginner', 'intermediate', 'advanced'])
    topic = st.text_input('Write your topic')
    new_chat = st.button('Start!')

    openai_api_key = st.text_input("OpenAI API Key", type="password")

    if new_chat:
        # Add the new chat to the list if the topic is not empty
        if topic:
            st.session_state.chat_list.append(topic)
            st.session_state.chat_list_option[topic] = {'language':language, 'level':level, 'topic':topic}
        else:
            st.warning("Please write a topic before starting a new chat!")

# Display the selected chat


# Main chat window
st.header(selected_chat.capitalize())
placeholder = st.empty()

if selected_chat == 'main' :
    st.write("This is chatbot that can be used to learn another language."
    "Make new chatting with left header."
    "You can input the topic you are interested in, and you can choose your language level."
    )

else :
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")

    # This is where you would add the functionality for sending/new messages, etc.
    else :
        # Create an OpenAI client.
        client = OpenAI(api_key=openai_api_key)

        # Create a session state variable to store the chat messages. This ensures that the
        # messages persist across reruns.
        if "messages" not in st.session_state: #['beginner', 'intermediate', 'advanced']
            st.session_state.messages = {}
        if selected_chat not in st.session_state.messages :
            text = f'You are chatting with user in context of '+ selected_chat
            if (st.session_state.chat_list_option[selected_chat]['level'] == 'beginner') :
                text += '. Talk with user in English, and suggest better chance for user to speak ' +st.session_state.chat_list_option[selected_chat]['language']
            else :
                text += '. Talk with user in '+st.session_state.chat_list_option[selected_chat]['language']+', and make user\'s message more natural'
            text += '. Make sure you search about newest information about ' + selected_chat + '.'
            st.session_state.messages[selected_chat] = [{'role':'system', 'content' : text}]
            st.write('prompt : ' + text)

        # Display the existing chat messages via `st.chat_message`.
        for message in st.session_state.messages[selected_chat][1:]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Create a chat input field to allow the user to enter a message. This will display
        # automatically at the bottom of the page.
        if prompt := st.chat_input("What is up?"):

            # Store and display the current prompt.
            st.session_state.messages[selected_chat].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API.
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[selected_chat]
                ],
                stream=True,
            )

            # Stream the response to the chat using `st.write_stream`, then store it in 
            # session state.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages[selected_chat].append({"role": "assistant", "content": response})
