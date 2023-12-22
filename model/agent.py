from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from .data import GREEK_GOD_DICT



class Agent:
    def __init__(self,api_key,api_org):
        self.llm = ChatOpenAI(temperature=0,openai_api_key=api_key,openai_organization=api_org,model_name="gpt-3.5-turbo-1106")
        self.llm_eval = ChatOpenAI(temperature=0,openai_api_key=api_key,openai_organization=api_org,model_name="gpt-4")

    def _jit_memory(self, message_history: []) -> ConversationBufferMemory:
        # assumes that message history is in ascending chronological order
        memory = ConversationBufferMemory(memory_key="chat_history")
        for i in message_history:
            if i["entity"] == "user":
                memory.chat_memory.add_user_message(i["message"])
            elif i["entity"] == "ai":
                memory.chat_memory.add_ai_message(i["message"])
            else:
                raise KeyError
        return memory
    
    def _background(self,god_name):
        return GREEK_GOD_DICT[god_name]
        
    def get_intro(self,god_name):
        god = self._background(god_name)
        return god['intro']
    
    def get_response(self,question,message_history,god_name,time_left):
        memory = self._jit_memory(message_history)
        god = self._background(god_name)
        if time_left>1:
            template = f"""Role: You are {god['name']}, {god['description']}. Adventurers are coming to you for help in their war. 
            You must evaluate their worthiness, and decide whether to help them or not. Your response should be medium length, 1-2 sentences.
            Your responses must be related to your divine domain and have the personality of {god['name']}.
            """+\
            """

            Previous conversation:
            {chat_history}
            
            New human question: {question}

            Response:
            """
        else:
            template = f"""Role: You are {god['name']}, {god['description']}. Adventurers are coming to you for help in their war. You must evaluate their worthiness, and decide whether to help them or not. 
            The portal is closing, you must say your final remarks and let them know you will decide by the end of the day.
            """+\
            """

            Previous conversation:
            {chat_history}
            
            New human question: {question}

            Response:
            """
        
        # You mustn't reveal your evaluation criteria to the adventurer. You must only ask indirect questions to understand their situation.
        # You have {time_left} minutes before the portal closes.
        # When they are out of time, let them know you will decide by the end of the day.
        # Your Evaluation Criteria: {god['evaluation']}
        prompt = PromptTemplate.from_template(template)
        conversation = LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=False,
            memory=memory
        )
        return conversation({"question":{question}})['text']
    
    def get_evaluation(self,message_history,god_name):
        memory = self._jit_memory(message_history)
        god = self._background(god_name)
        template = f"""Role: You are {god['name']}, {god['description']}. This adventurer for help in their war. You must evaluate their worthiness, and decide whether to help them or not. 
        It is the end of the day. You must make your decision. Give them a score from 1-5 for each of the following criteria and an overall score based on your previous conversation.
        Your Evaluation Criteria: {god['evaluation']}
        """+\
        """

        Previous conversation:
        {chat_history}
        
        New human question: {question}

        Response:
        """
        prompt = PromptTemplate.from_template(template)
        conversation = LLMChain(
            llm=self.llm_eval,
            prompt=prompt,
            verbose=False,
            memory=memory
        )
        ans= conversation({"question":{"Am I worthy?"}})['text']
        print(ans)
        return ans