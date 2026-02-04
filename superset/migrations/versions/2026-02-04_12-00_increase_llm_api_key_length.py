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
"""increase_llm_api_key_length

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2026-02-04 12:00:00.000000

This migration increases the api_key column length in the llm_connection table
from VARCHAR(100) to TEXT to accommodate longer API keys from providers like
Anthropic and OpenAI, which often exceed 100 characters.

"""

# revision identifiers, used by Alembic.
revision = "b1c2d3e4f5g6"
down_revision = "a1b2c3d4e5f6"

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql


def upgrade():
    # Change api_key column from VARCHAR(100) to TEXT
    with op.batch_alter_table("llm_connection") as batch_op:
        batch_op.alter_column(
            "api_key",
            existing_type=sa.VARCHAR(length=100),
            type_=sa.Text().with_variant(mysql.TEXT(), "mysql"),
            existing_nullable=False,
        )


def downgrade():
    # Revert api_key column from TEXT back to VARCHAR(100)
    # WARNING: This may truncate data if any keys are longer than 100 characters
    with op.batch_alter_table("llm_connection") as batch_op:
        batch_op.alter_column(
            "api_key",
            existing_type=sa.Text(),
            type_=sa.VARCHAR(length=100),
            existing_nullable=False,
        )
