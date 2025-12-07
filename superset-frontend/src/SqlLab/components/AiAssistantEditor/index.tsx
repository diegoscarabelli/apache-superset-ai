/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import {
  ChangeEvent,
} from 'react';

import { useDispatch, useSelector } from 'react-redux';

import { css, t, styled } from '@superset-ui/core';

import { Button, Input, Icons } from '@superset-ui/core/components';
import {
    LOG_ACTIONS_AI_ASSISTANT_OPENED
} from 'src/logger/LogUtils';
import useLogAction from 'src/logger/useLogAction';

import { setGenerateSqlPrompt } from 'src/SqlLab/actions/sqlLab';
import { SqlLabRootState } from 'src/SqlLab/types';


export interface AiAssistantEditorProps {
  queryEditorId: string;
  onGenerateSql: (prompt: string) => void;
  isGeneratingSql: boolean;
  schema?: string | string[];
  disabledMessage?: string;
}

const StyledContainer = styled.div`
  ${({ theme }) => css`
    border: 1px solid ${theme.colorBorder};
    border-bottom: 0;
    background: ${theme.colorBgContainer};
  `}
`;

const StyledToolbar = styled.div`
  ${({ theme }) => css`
    padding: ${theme.sizeUnit * 2}px;
    display: flex;
    align-items: center;
    gap: ${theme.sizeUnit * 2}px;

    input {
      flex: 1;
      min-width: 300px;
    }

    .label {
      flex-shrink: 0;
      width: ${theme.sizeUnit * 25}px;
      color: ${theme.colorText};
      font-size: ${theme.fontSize}px;
    }
  `}
`;

const DisabledMessage = styled.div`
  ${({ theme }) => css`
    color: ${theme.colorError};
    border-top: 1px solid ${theme.colorBorder};
    font-size: ${theme.fontSizeSM}px;
    padding: ${theme.sizeUnit * 2}px;
    display: flex;
    align-items: center;
    column-gap: ${theme.sizeUnit}px;
  `}
`;

const SelectedSchemaMessage = styled.div`
  ${({ theme }) => css`
    color: ${theme.colorText};
    border-top: 1px solid ${theme.colorBorder};
    font-size: ${theme.fontSizeSM}px;
    padding: ${theme.sizeUnit * 2}px;
    display: flex;
    align-items: center;
    column-gap: ${theme.sizeUnit}px;
  `}
`;

const onClick = (
  logAction: (name: string, payload: Record<string, any>) => void,
): void => {
  logAction(LOG_ACTIONS_AI_ASSISTANT_OPENED, { shortcut: false });
};

const AiAssistantEditor = ({
  queryEditorId,
  onGenerateSql,
  isGeneratingSql = false,
  schema = [],
  disabledMessage,
}: AiAssistantEditorProps) => {
  const dispatch = useDispatch();
  const logAction = useLogAction({ queryEditorId });

  const changePrompt = (event: ChangeEvent<HTMLInputElement>) => {
    dispatch(setGenerateSqlPrompt(queryEditorId, event.target.value));
  };

  const prompt = useSelector((state: SqlLabRootState) => {
    const queryEditor = state.sqlLab.queryEditors.find(qe => qe.id === queryEditorId);
    if (queryEditor) {
      return queryEditor.queryGenerator?.prompt || '';
    }
    return '';
  });

  const isDisabled = isGeneratingSql || !!disabledMessage;

  return (
    <StyledContainer>
      <StyledToolbar>
        <span className="label">AI Assist</span>
        <Input
          onChange={changePrompt}
          value={prompt}
          className="form-control input-sm"
          placeholder={t('How many employees are located in Bath?')}
          disabled={isDisabled}
          onKeyDown={(e) => {
            if (!isDisabled && e.key === 'Enter') {
              e.preventDefault();
              onClick(logAction);
              onGenerateSql(prompt);
            }
          }}
        />
        <Button
          buttonSize="small"
          buttonStyle="secondary"
          icon={<Icons.BulbOutlined />}
          onClick={() => {
            onClick(logAction);
            onGenerateSql(prompt);
          }}
          tooltip={t('Generate SQL with AI') as string}
          disabled={isDisabled}
        >
          {isGeneratingSql ? t('Generating...') : t('Generate SQL')}
        </Button>
      </StyledToolbar>
      {disabledMessage ? (
        <DisabledMessage>
          <Icons.InfoCircleOutlined />
          {disabledMessage}
        </DisabledMessage>
      ) : (() => {
          // Check if schema has meaningful content (not empty string or array of empty strings)
          const hasSchema = schema &&
            (Array.isArray(schema)
              ? schema.filter(s => s && s.trim()).length > 0
              : schema.trim().length > 0);

          return hasSchema ? (
            <SelectedSchemaMessage>
              <Icons.InfoCircleOutlined />
              {`Selecting schema will restrict the AI to generate SQL for only the selected schema. This will increase costs due to skipping the AI cache. Currently selected: ${Array.isArray(schema) ? schema.filter(s => s && s.trim()).join(', ') : schema}`}
            </SelectedSchemaMessage>
          ) : null;
        })()}
    </StyledContainer>
  );
};

export default AiAssistantEditor;
