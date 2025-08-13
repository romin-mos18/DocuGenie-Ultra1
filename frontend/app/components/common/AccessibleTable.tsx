'use client';

import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
} from '@mui/material';
import { useAccessibility } from '../../../lib/hooks/useAccessibility';

interface AccessibleTableProps {
  data: any[];
  columns: {
    key: string;
    label: string;
    render?: (value: any, row: any) => React.ReactNode;
  }[];
  caption?: string;
  'aria-label'?: string;
  'aria-describedby'?: string;
}

export default function AccessibleTable({
  data,
  columns,
  caption,
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedBy,
}: AccessibleTableProps) {
  const { announceLoading } = useAccessibility();

  React.useEffect(() => {
    if (data.length > 0) {
      announceLoading(`Table loaded with ${data.length} rows`);
    }
  }, [data.length, announceLoading]);

  const tableAriaProps = {
    'aria-label': ariaLabel || caption,
    'aria-describedby': ariaDescribedBy,
  };

  return (
    <Box sx={{ width: '100%', overflow: 'auto' }}>
      <TableContainer component={Paper} elevation={1}>
        <Table
          sx={{ minWidth: 650 }}
          {...tableAriaProps}
        >
          {caption && (
            <caption style={{ padding: '8px', fontWeight: 'bold' }}>
              {caption}
            </caption>
          )}
          
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.key}
                  component="th"
                  scope="col"
                  sx={{ fontWeight: 'bold' }}
                >
                  {column.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          
          <TableBody>
            {data.map((row, index) => (
              <TableRow
                key={index}
                sx={{ '&:nth-of-type(odd)': { backgroundColor: 'action.hover' } }}
              >
                {columns.map((column) => (
                  <TableCell key={column.key}>
                    {column.render
                      ? column.render(row[column.key], row)
                      : row[column.key]}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
