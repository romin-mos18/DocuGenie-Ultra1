'use client';

import React from 'react';
import UniversalDocumentDetails from './UniversalDocumentDetails';

interface DocumentDetailsProps {
  documentId: number;
}

/**
 * DocumentDetails Component
 * 
 * This component serves as a wrapper around UniversalDocumentDetails
 * to maintain compatibility with existing code while providing
 * the enhanced, bulletproof document analysis display.
 */
export default function DocumentDetails({ documentId }: DocumentDetailsProps) {
  return <UniversalDocumentDetails documentId={documentId} />;
}
