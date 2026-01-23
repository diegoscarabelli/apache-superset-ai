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
"""update_gemini_model_ids

Revision ID: a1b2c3d4e5f6
Revises: abc123def456
Create Date: 2026-01-23 19:30:00.000000

This migration updates deprecated Gemini model IDs in the llm_connection table.
Google deprecated Gemini 2.0 and below models (shutdown March 31, 2026).
Old model IDs with 'models/' prefix are updated to new format without prefix,
and deprecated models are migrated to their closest equivalent.

Model mapping:
- models/gemini-1.5-flash-002 -> gemini-2.5-flash
- models/gemini-2.0-flash -> gemini-2.5-flash
- models/gemini-2.0-flash-thinking-exp -> gemini-2.5-flash
- models/gemini-1.5-pro-002 -> gemini-2.5-pro
- models/gemini-2.0-pro-exp -> gemini-2.5-pro
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "abc123def456"

# Mapping of old model IDs to new model IDs
MODEL_MAPPING = {
    "models/gemini-1.5-flash-002": "gemini-2.5-flash",
    "models/gemini-2.0-flash": "gemini-2.5-flash",
    "models/gemini-2.0-flash-thinking-exp": "gemini-2.5-flash",
    "models/gemini-1.5-pro-002": "gemini-2.5-pro",
    "models/gemini-2.0-pro-exp": "gemini-2.5-pro",
}


def upgrade():
    # Update each deprecated model ID to its new equivalent
    connection = op.get_bind()

    for old_model, new_model in MODEL_MAPPING.items():
        connection.execute(
            sa.text(
                "UPDATE llm_connection SET model = :new_model "
                "WHERE provider = 'Gemini' AND model = :old_model"
            ),
            {"old_model": old_model, "new_model": new_model},
        )


def downgrade():
    # Reverse mapping - restore old model IDs
    # Note: This is a best-effort downgrade; the old models may not work
    connection = op.get_bind()

    # Create reverse mapping (new -> first old that mapped to it)
    reverse_mapping = {
        "gemini-2.5-flash": "models/gemini-2.0-flash",
        "gemini-2.5-pro": "models/gemini-2.0-pro-exp",
    }

    for new_model, old_model in reverse_mapping.items():
        connection.execute(
            sa.text(
                "UPDATE llm_connection SET model = :old_model "
                "WHERE provider = 'Gemini' AND model = :new_model"
            ),
            {"old_model": old_model, "new_model": new_model},
        )
