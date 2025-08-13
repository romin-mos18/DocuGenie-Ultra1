# Accessibility Guide

This document outlines the accessibility features and best practices implemented in the DocuGenie Ultra frontend.

## Overview

The application follows WCAG 2.1 AA standards and implements comprehensive accessibility features to ensure all users can effectively interact with the system.

## Key Accessibility Features

### 1. Keyboard Navigation

- **Skip Links**: Users can skip to main content using the skip link at the top of the page
- **Focus Management**: Proper focus indicators and logical tab order throughout the application
- **Focus Trapping**: Modal dialogs and popups trap focus to prevent users from accidentally navigating outside
- **Keyboard Shortcuts**: Common keyboard shortcuts (Enter, Escape, Arrow keys) are supported

### 2. Screen Reader Support

- **ARIA Labels**: All interactive elements have descriptive ARIA labels
- **Live Regions**: Dynamic content updates are announced to screen readers
- **Semantic HTML**: Proper use of heading hierarchy and semantic elements
- **Form Labels**: All form inputs have associated labels and error descriptions

### 3. Visual Accessibility

- **High Contrast Mode**: Support for high contrast display preferences
- **Reduced Motion**: Respects user preferences for reduced motion
- **Color Contrast**: All text meets WCAG AA contrast requirements
- **Focus Indicators**: Clear visual focus indicators for all interactive elements

### 4. Form Accessibility

- **Error Handling**: Clear error messages with proper ARIA attributes
- **Required Fields**: Visual and programmatic indication of required fields
- **Validation**: Real-time validation with accessible error announcements
- **Help Text**: Contextual help text for complex form fields

## Components

### SkipLink

Provides keyboard users with a way to skip navigation and go directly to main content.

```tsx
import SkipLink from '@/components/common/SkipLink';

// Automatically included in Layout component
```

### FocusTrap

Traps focus within modal dialogs and popups to prevent accidental navigation.

```tsx
import FocusTrap from '@/components/common/FocusTrap';

<FocusTrap onEscape={handleClose}>
  <ModalContent />
</FocusTrap>
```

### Accessibility Utilities

The `lib/accessibility.ts` file provides utility functions for:

- Focus management
- Keyboard navigation
- Live region announcements
- ARIA helpers
- Color contrast calculations
- Screen reader utilities

## Testing

### Automated Testing

We use `jest-axe` for automated accessibility testing:

```bash
npm test -- --testPathPattern=accessibility
```

### Manual Testing Checklist

- [ ] Navigate using only keyboard (Tab, Shift+Tab, Enter, Escape)
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Verify color contrast meets WCAG AA standards
- [ ] Test with high contrast mode enabled
- [ ] Test with reduced motion preferences
- [ ] Verify all images have alt text
- [ ] Check form validation accessibility

## Best Practices

### 1. Semantic HTML

Always use semantic HTML elements:

```tsx
// Good
<main id="main-content">
  <h1>Page Title</h1>
  <section aria-labelledby="section-title">
    <h2 id="section-title">Section Title</h2>
  </section>
</main>

// Avoid
<div>
  <div>Page Title</div>
  <div>Section Title</div>
</div>
```

### 2. ARIA Attributes

Use ARIA attributes appropriately:

```tsx
// Good
<button 
  aria-expanded={isOpen}
  aria-controls="menu"
  aria-label="Toggle menu"
>
  Menu
</button>

// Avoid
<button>Menu</button>
```

### 3. Form Accessibility

Ensure forms are accessible:

```tsx
// Good
<TextField
  label="Email"
  aria-describedby="email-error email-help"
  aria-invalid={hasError}
  error={hasError}
  helperText={errorMessage}
/>

// Avoid
<input type="email" />
```

### 4. Focus Management

Manage focus properly:

```tsx
// Good
const handleModalOpen = () => {
  setModalOpen(true);
  // Focus first interactive element
  setTimeout(() => {
    const firstButton = document.querySelector('[role="dialog"] button');
    firstButton?.focus();
  }, 100);
};

// Avoid
const handleModalOpen = () => {
  setModalOpen(true);
};
```

## Color Palette

Our color palette is designed to meet WCAG AA contrast requirements:

- Primary text: #000000 on #FFFFFF (21:1 ratio)
- Secondary text: #666666 on #FFFFFF (4.5:1 ratio)
- Links: #1976d2 on #FFFFFF (4.5:1 ratio)
- Error text: #d32f2f on #FFFFFF (4.5:1 ratio)

## Responsive Design

All accessibility features work across different screen sizes:

- Mobile: Touch targets are at least 44x44px
- Tablet: Maintains keyboard navigation
- Desktop: Full keyboard and mouse support

## Browser Support

Accessibility features are tested and supported in:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Screen Reader Support

Tested with:

- NVDA (Windows)
- JAWS (Windows)
- VoiceOver (macOS)
- TalkBack (Android)
- VoiceOver (iOS)

## Performance Considerations

- Accessibility features are optimized for performance
- ARIA live regions are used sparingly to avoid excessive announcements
- Focus management is debounced to prevent performance issues
- Color contrast calculations are cached

## Future Improvements

- [ ] Add more comprehensive keyboard shortcuts
- [ ] Implement voice navigation support
- [ ] Add haptic feedback for mobile users
- [ ] Enhance screen reader announcements
- [ ] Add accessibility preferences panel

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/TR/wai-aria-practices/)
- [WebAIM Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [axe-core Documentation](https://github.com/dequelabs/axe-core)
