import React from 'react';

// Performance optimization utilities

// Debounce function for performance optimization
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// Throttle function for performance optimization
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

// Lazy loading utility
export const lazyLoad = (importFunc: () => Promise<any>) => {
  return {
    component: importFunc,
    loading: () => React.createElement('div', null, 'Loading...'),
  };
};

// Image optimization utility
export const optimizeImage = (src: string, width: number, height: number) => {
  // Add image optimization parameters
  const params = new URLSearchParams({
    w: width.toString(),
    h: height.toString(),
    q: '80', // quality
    fm: 'webp', // format
  });
  
  return `${src}?${params.toString()}`;
};

// Bundle size optimization
export const preloadComponent = (componentPath: string) => {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.as = 'script';
  link.href = componentPath;
  document.head.appendChild(link);
};

// Memory management
export const cleanupMemory = () => {
  // Clear any cached data
  if ('caches' in window) {
    caches.keys().then(names => {
      names.forEach(name => {
        caches.delete(name);
      });
    });
  }
  
  // Clear localStorage if needed
  // localStorage.clear(); // Uncomment if needed
};

// Performance monitoring
export const measurePerformance = (name: string, fn: () => void) => {
  const start = performance.now();
  fn();
  const end = performance.now();
  console.log(`${name} took ${end - start} milliseconds`);
};

// Bundle size analyzer
export const getBundleSize = () => {
  if (typeof window !== 'undefined' && 'performance' in window) {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    return {
      totalSize: navigation.transferSize,
      decodedSize: navigation.decodedBodySize,
      encodedSize: navigation.encodedBodySize,
    };
  }
  return null;
};

// Component lazy loading with error boundary
export const withErrorBoundary = (Component: React.ComponentType<any>) => {
  return class ErrorBoundary extends React.Component<any, { hasError: boolean }> {
    constructor(props: any) {
      super(props);
      this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: any) {
      return { hasError: true };
    }

    componentDidCatch(error: any, errorInfo: any) {
      console.error('Error caught by boundary:', error, errorInfo);
    }

    render() {
      if (this.state.hasError) {
        return React.createElement('div', null, 'Something went wrong. Please try again.');
      }

      return React.createElement(Component, this.props);
    }
  };
};

// Intersection Observer for lazy loading
export const useIntersectionObserver = (
  ref: React.RefObject<HTMLElement>,
  options: IntersectionObserverInit = {}
) => {
  const [isIntersecting, setIsIntersecting] = React.useState(false);

  React.useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
    }, options);

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [ref, options]);

  return isIntersecting;
};

// Virtual scrolling utility
export const useVirtualScrolling = (
  items: any[],
  itemHeight: number,
  containerHeight: number
) => {
  const [scrollTop, setScrollTop] = React.useState(0);

  const visibleItems = React.useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    );

    return items.slice(startIndex, endIndex).map((item, index) => ({
      ...item,
      index: startIndex + index,
      style: {
        position: 'absolute',
        top: (startIndex + index) * itemHeight,
        height: itemHeight,
      },
    }));
  }, [items, itemHeight, containerHeight, scrollTop]);

  return {
    visibleItems,
    totalHeight: items.length * itemHeight,
    onScroll: (e: React.UIEvent<HTMLDivElement>) => {
      setScrollTop(e.currentTarget.scrollTop);
    },
  };
};
