'use client';

import React from 'react';
import DocumentDetails from '../../components/documents/DocumentDetails';

interface DocumentPageProps {
  params: {
    id: string;
  };
}

export default function DocumentPage({ params }: DocumentPageProps) {
  return <DocumentDetails documentId={parseInt(params.id, 10)} />;
}
