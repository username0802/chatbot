import streamlit as st
from openai import OpenAI
import bing

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
    bing_api_key = st.text_input("bing API Key", type="password")

    if new_chat:
        # Add the new chat to the list if the topic is not empty
        if topic:
            if topic in st.session_state.chat_list :
                st.warning("Chatting already exists. Please choose another topic!")
            else :
                st.session_state.chat_list.append(topic)
                st.session_state.chat_list_option[topic] = {'language':language, 'level':level, 'topic':topic}
        else:
            st.warning("Please write a topic before starting a new chat!")

# Display the selected chat


# Main chat window
st.header(selected_chat.capitalize())
placeholder = st.empty()

if selected_chat == 'main' :
    st.write("This is chatbot that can be used to learn another language.",
             "Make new chatting with left header.",
             "You can input the topic you are interested in, and you can choose your language level.")
    st.write("beginner : If you send text in english, it would translate it into selected language.")
    st.write("intermediate / advanced : It is option for people who can free-talk in selected language. chatbot would fix your sentences more naturally.")
    placeholder = st.empty()
    st.write("You can also fix prompt in the \"option\" tab.")

    

else :
    chat, option, fixing = st.tabs(['chatting', 'option', 'fixed inputs'])

    with chat :

        if "messages" not in st.session_state: #['beginner', 'intermediate', 'advanced']
            st.session_state.messages = {}
            st.session_state.fix_messages = {}
        if selected_chat not in st.session_state.messages :
            text = f'you are chatting with user in context of '+ selected_chat
            if (st.session_state.chat_list_option[selected_chat]['level'] == 'beginner') :
                text += '. Talk with user in English, and suggest better chance for user to speak ' +st.session_state.chat_list_option[selected_chat]['language']
            else :
                text += '. Talk with user in '+st.session_state.chat_list_option[selected_chat]['language']
            text += ". You don't have to answer too long. You are friend-like chat bot."
            st.session_state.messages[selected_chat] = [{'role':'system', 'content' : text}]

            if st.session_state.chat_list_option[selected_chat]['level'] == 'beginner' :
                fixing_require = f"You are translator. Translate input texts in {st.session_state.chat_list_option[selected_chat]['language']}. you are not supposed to answer, but translate the input. TRANSLATE ENGLISH TO {st.session_state.chat_list_option[selected_chat]['language']}."
            else :
                fixing_require = "You are writing assistant. You are not supposed to answer the question, but fixing the inpuy text."
            st.session_state.fix_messages[selected_chat] = [{'role':'system', 'content' : fixing_require}]



            # Display the existing chat messages via `st.chat_message`.
            for message in st.session_state.messages[selected_chat][1:]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if not openai_api_key or not bing_api_key:
            st.info("Please add your API key to continue.", icon="🗝️")
        # This is where you would add the functionality for sending/new messages, etc.
        else :
            # Create an OpenAI client.
            client = OpenAI(api_key=openai_api_key)


            for message in st.session_state.messages[selected_chat][1:]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            # Create a session state variable to store the chat messages. This ensures that the
            # messages persist across reruns.

            # Create a chat input field to allow the user to enter a message. This will display
            # automatically at the bottom of the page.
            if prompt := st.chat_input("What is up?"):

                result_texts = bing.get_relevant_texts(f"{selected_chat} {prompt}", bing_api_key)

                # Store and display the current prompt.
                prompt_with_context = f"""
                here is the context about {selected_chat}.

                answer in context below :
                {str(result_texts)}

                Question : 
                {prompt}
                """

                with st.chat_message("user"):
                    st.markdown(prompt)

                if st.session_state.chat_list_option[selected_chat]['level'] == 'beginner' :
                    prompt_for_fix = "translate this in " + st.session_state.chat_list_option[selected_chat]['language'] + ". " + prompt

                st.session_state.fix_messages[selected_chat].append({"role": "user", "content": prompt_for_fix})
                st.session_state.messages[selected_chat].append({"role": "user", "content": prompt_with_context})

                fix_stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.fix_messages[selected_chat]
                    ],
                    stream=True,
                )
                
                with st.chat_message("assistant"):
                    response = st.write_stream(fix_stream)
                st.session_state.fix_messages[selected_chat].append({"role": "assistant", "content": response})


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
                st.session_state.messages[selected_chat][-2]['content'] = prompt

                


    with option :
        st.write("Your option :")
        st.write("-selected language :", st.session_state.chat_list_option[selected_chat]['language'],
        " \n -selected level :",st.session_state.chat_list_option[selected_chat]['level'])

        st.write("".join(st.session_state.messages[selected_chat][0]['content'].split("chat bot.")[1:]))
        fixed_prompt = st.text_input("add text into your prompt")
        if fixed_prompt :
            st.session_state.messages[selected_chat][0]['content'] += fixed_prompt

    with fixing :
        for message in st.session_state.fix_messages[selected_chat][1:]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
