# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import json
import logging

import openai

from typing import List

from superset.daos.database import DatabaseDAO
from superset.llms.openai import OpenAiLlm


logger = logging.getLogger(__name__)


class ThauraLlm(OpenAiLlm):
    llm_type = "Thaura"

    @staticmethod
    def get_models():
        return {
            'thaura': {
                'name': 'Thaura',
                'input_token_limit': 128000
            },
        }

    def _trim_markdown(self, text: str) -> str:
        """
        Override to handle Thaura's <think> tags in addition to markdown.
        Thaura may wrap reasoning in <think>...</think> tags before the SQL.
        """
        # First, strip any <think> tags and their content
        if '<think>' in text and '</think>' in text:
            # If we have both opening and closing tags, remove everything up to closing tag
            think_end = text.index('</think>')
            text = text[think_end + 8:].strip()

        # Then apply the parent class's markdown trimming
        return super()._trim_markdown(text)

    def generate_sql(self, prompt: str, history: str, schemas: List[str] | None) -> str:
        """
        Generate SQL from a user prompt using the Thaura.ai API (OpenAI-compatible).
        """
        db = DatabaseDAO.find_by_id(self.pk, True)
        if not db:
            logger.error(f"Database {self.pk} not found.")
            return

        if not db.llm_connection.enabled:
            logger.error(f"LLM is not enabled for database {self.pk}.")
            return

        if not db.llm_connection.provider == self.llm_type:
            logger.error(f"LLM provider is not {self.llm_type} for database {self.pk}.")
            return

        llm_api_key = db.llm_connection.api_key
        if not llm_api_key:
            logger.error(f"API key not set for database {self.pk}.")
            return

        llm_model = db.llm_connection.model
        if not llm_model:
            logger.error(f"Model not set for database {self.pk}.")
            return

        logger.info(f"Using API key {llm_api_key} and model {llm_model} for database {self.pk}")

        user_instructions = db.llm_context_options.instructions

        # Create OpenAI client with Thaura.ai base URL
        client = openai.OpenAI(
            api_key=llm_api_key,
            base_url="https://backend.thaura.ai/v1"
        )

        # Compose system prompt and context
        system_prompt = user_instructions if user_instructions else self.get_system_instructions(self.dialect)
        context_json = json.dumps([schema for schema in self.context if not schemas or schema['schema_name'] in schemas])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Database metadata:\n{context_json}"}
        ]
        if history:
            messages.append({"role": "user", "content": history})
        messages.append({"role": "user", "content": prompt})

        logger.info(f"Thaura request - model: {llm_model}, context size: {len(context_json)} chars, total message count: {len(messages)}")

        try:
            response = client.chat.completions.create(
                model=llm_model,
                messages=messages,
                stream=False,  # Explicitly disable streaming
            )
            logger.info(f"Thaura API response type: {type(response)}")
        except Exception as e:
            logger.error(f"Thaura API error: {e}")
            return f"-- Failed to generate SQL: {str(e)}"

        if not response or not response.choices or len(response.choices) < 1:
            logger.error("No response from Thaura API.")
            return "-- Failed to generate SQL: No response from Thaura API."

        reply = response.choices[0].message.content.strip()
        sql = self._trim_markdown(reply)
        if not sql:
            return "-- Unable to find valid SQL in the LLM response"

        logger.info(f"Generated SQL: {sql}")
        return sql
