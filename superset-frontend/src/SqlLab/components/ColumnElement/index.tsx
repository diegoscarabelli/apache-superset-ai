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
import { ReactNode } from 'react';
import { ClassNames } from '@emotion/react';
import { styled, useTheme, t } from '@superset-ui/core';
import { Flex, Tooltip } from '@superset-ui/core/components';
import {
  KeyOutlined,
  LinkOutlined,
  BookOutlined,
  CommentOutlined,
} from '@ant-design/icons';

const StyledTooltip = (props: any) => {
  const theme = useTheme();
  return (
    <ClassNames>
      {({ css }) => (
        <Tooltip
          overlayClassName={css`
            .ant-tooltip-inner {
              max-width: ${theme.sizeUnit * 125}px;
              word-wrap: break-word;
              text-align: center;

              pre {
                background: transparent;
                border: none;
                text-align: left;
                color: ${theme.colorBgLayout};
                font-size: ${theme.fontSizeXS}px;
              }

              p {
                text-align: left;
              }
            }
          `}
          {...props}
        />
      )}
    </ClassNames>
  );
};

const Hr = styled.hr`
  margin-top: ${({ theme }) => theme.sizeUnit * 1.5}px;
`;

const iconComponentMap = {
  pk: KeyOutlined,
  fk: LinkOutlined,
  index: BookOutlined,
  comment: CommentOutlined,
};

const tooltipTitleMap = {
  pk: t('Primary key'),
  fk: t('Foreign key'),
  index: t('Index'),
  comment: t('Comment'),
};

export type ColumnKeyTypeType = keyof typeof tooltipTitleMap;

interface ColumnElementProps {
  column: {
    name: string;
    keys?: { type: ColumnKeyTypeType }[];
    type: string;
    comment?: string;
  };
}

const NowrapDiv = styled.div`
  white-space: nowrap;
`;

const ColumnElement = ({ column }: ColumnElementProps) => {
  let columnName: ReactNode = column.name;
  let icons: ReactNode[] = [];
  if (column.keys && column.keys.length > 0) {
    columnName = <strong>{column.name}</strong>;
    icons = column.keys.map((key, i) => {
      const IconComponent = iconComponentMap[key.type];
      return (
        <span key={i} className="ColumnElement" style={{ marginLeft: 8 }}>
          <StyledTooltip
            placement="right"
            title={
              <>
                <strong>{tooltipTitleMap[key.type]}</strong>
                <Hr />
                <pre className="text-small">
                  {JSON.stringify(key, null, '  ')}
                </pre>
              </>
            }
          >
            <IconComponent style={{ color: 'rgba(0, 0, 0, 0.45)' }} />
          </StyledTooltip>
        </span>
      );
    });
  }
  if (column.comment) {
    icons.push(
      <span key="comment" className="ColumnElement" style={{ marginLeft: 8 }}>
        <StyledTooltip
          placement="right"
          title={
            <>
              <strong>{tooltipTitleMap.comment}</strong>
              <Hr />
              <p className="text-small">{column.comment}</p>
            </>
          }
        >
          <CommentOutlined style={{ color: 'rgba(0, 0, 0, 0.45)' }} />
        </StyledTooltip>
      </span>,
    );
  }
  return (
    <Flex align="center" justify="space-between">
      <div data-test="col-name">
        {columnName}
        {icons}
      </div>
      <NowrapDiv className="text-muted">
        <small> {column.type}</small>
      </NowrapDiv>
    </Flex>
  );
};

export default ColumnElement;
