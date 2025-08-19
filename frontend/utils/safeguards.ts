/**
 * React rendering safeguards to prevent object rendering errors
 */

/**
 * Safely extract string value from AI analysis data
 */
export function safeStringValue(value: any, fallback: string = ''): string {
  if (typeof value === 'string') {
    return value;
  }
  if (typeof value === 'number') {
    return value.toString();
  }
  if (typeof value === 'object' && value !== null) {
    // Handle language analysis objects
    if (value.primary_language) {
      return value.primary_language;
    }
    // Handle other nested string values
    if (value.value) {
      return value.value;
    }
    if (value.text) {
      return value.text;
    }
    // If it's an object, don't render it directly
    return fallback;
  }
  return fallback;
}

/**
 * Safely extract number value from AI analysis data
 */
export function safeNumberValue(value: any, fallback: number = 0): number {
  if (typeof value === 'number') {
    return value;
  }
  if (typeof value === 'string') {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? fallback : parsed;
  }
  if (typeof value === 'object' && value !== null) {
    // Handle confidence objects
    if (typeof value.confidence === 'number') {
      return value.confidence;
    }
    if (typeof value.value === 'number') {
      return value.value;
    }
  }
  return fallback;
}

/**
 * Safely extract language from AI analysis
 */
export function safeLanguage(language: any): string {
  if (typeof language === 'string') {
    return language;
  }
  if (typeof language === 'object' && language !== null) {
    return language.primary_language || language.language_code || 'EN';
  }
  return 'EN';
}

/**
 * Safely extract entity count from AI analysis
 */
export function safeEntityCount(entities: any): number {
  if (typeof entities === 'number') {
    return entities;
  }
  if (typeof entities === 'object' && entities !== null) {
    if (typeof entities.entity_count === 'number') {
      return entities.entity_count;
    }
    if (typeof entities.length === 'number') {
      return entities.length;
    }
    // Count object keys if it's an entities object
    if (entities.entities && typeof entities.entities === 'object') {
      return Object.keys(entities.entities).reduce((count, key) => {
        const entityList = entities.entities[key];
        return count + (Array.isArray(entityList) ? entityList.length : 0);
      }, 0);
    }
  }
  return 0;
}

/**
 * Enhanced safe property accessor for nested objects
 */
export const safeGet = (obj: any, path: string, defaultValue: any = null) => {
  try {
    return path.split('.').reduce((current, prop) => current?.[prop], obj) ?? defaultValue;
  } catch {
    return defaultValue;
  }
};

/**
 * Safe array accessor
 */
export const safeArray = (arr: any): any[] => {
  return Array.isArray(arr) ? arr : [];
};

/**
 * Document type configuration helper
 */
export const getDocumentTypeConfig = (documentType: string) => {
  const configs = {
    medical_report: { color: 'primary', label: 'Medical Report', category: 'medical' },
    lab_result: { color: 'success', label: 'Lab Result', category: 'medical' },
    financial_report: { color: 'warning', label: 'Financial Report', category: 'financial' },
    bank_statement: { color: 'info', label: 'Bank Statement', category: 'financial' },
    appointment: { color: 'secondary', label: 'Appointment', category: 'medical' },
    patient_record: { color: 'primary', label: 'Patient Record', category: 'medical' },
    insurance_claim: { color: 'warning', label: 'Insurance Claim', category: 'insurance' },
    prescription: { color: 'success', label: 'Prescription', category: 'medical' },
    certificate: { color: 'info', label: 'Certificate', category: 'legal' },
    contract: { color: 'error', label: 'Contract', category: 'legal' },
    billing: { color: 'warning', label: 'Billing Document', category: 'financial' },
    other: { color: 'default', label: 'Document', category: 'general' },
  };
  
  return configs[documentType as keyof typeof configs] || configs.other;
};

/**
 * Check if document is a specific category
 */
export const isDocumentCategory = (documentType: string, category: string): boolean => {
  const config = getDocumentTypeConfig(documentType);
  return config.category === category;
};

/**
 * Format confidence as percentage with 2 decimal places
 */
export const formatConfidence = (confidence: number): string => {
  if (typeof confidence !== 'number' || isNaN(confidence)) {
    return '0.00%';
  }
  return (confidence * 100).toFixed(2) + '%';
};

/**
 * Format file size
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Safe date formatting
 */
export const safeFormatDate = (date: any): string => {
  try {
    if (!date) return 'N/A';
    const dateObj = new Date(date);
    if (isNaN(dateObj.getTime())) return 'Invalid Date';
    return dateObj.toLocaleDateString();
  } catch {
    return 'N/A';
  }
};
