from typing import List, Dict, Any
from ..agents.agent_1 import agent_1_identifies
from ..agents.agent_2 import agent_2_calculates
from ..agents.agent_3 import agent_3_validates
from ..services.vector_service import PineconeService
import logging
import traceback

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self):
        self.vector_service = PineconeService()
        
    async def process_user_input(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Process user input through the agent pipeline.
        """
        try:
            logger.debug(f"Processing user input: {user_input}")
            parsed_json_list = agent_1_identifies(user_input)
            logger.debug(f"Agent 1 output: {parsed_json_list}")
            
            results = []
            pinecone_index = self.vector_service.initialize_index()
            logger.debug("Initialized Pinecone index")
            
            for parsed_json in parsed_json_list:
                logger.debug(f"Processing parsed JSON: {parsed_json}")
                macros = agent_2_calculates(parsed_json)
                logger.debug(f"Agent 2 output: {macros}")
                
                validated_macros = agent_3_validates(macros)
                logger.debug(f"Agent 3 output: {validated_macros}")
                
                await self.vector_service.add_entry(validated_macros, pinecone_index)
                results.append(validated_macros)
            
            return results
        except Exception as e:
            logger.error(f"Error in process_user_input: {str(e)}")
            logger.error(traceback.format_exc())
            raise
