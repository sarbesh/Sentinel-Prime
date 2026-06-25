# UI Architecture for SENTINEL PRIME

## Overview
SENTINEL PRIME is a unified application targeting both web and mobile platforms. The architecture leverages React for web and React Native for mobile, maximizing code sharing while respecting platform-specific capabilities and constraints.

## Technology Stack
- **Web**: React 18+, React Router v6, Styled Components or Tailwind CSS
- **Mobile**: React Native 0.70+, React Navigation, Styled Components or NativeBase
- **Shared**: JavaScript/TypeScript, monorepo structure (e.g., Nx or Turborepo), Zustand for state management, React Query for server state, Axios for API communication

## Code Sharing Strategy
We adopt a monorepo with the following structure:
```
/packages
  /web          // React web application
  /mobile       // React Native mobile application
  /shared       // Platform-agnostic code: utilities, hooks, services, types, constants
  /ui           // Shared UI component library (designed for both platforms)
  /config       // Shared configurations (ESLint, Prettier, TypeScript, etc.)
```

### Sharing Principles
1. **Business Logic**: All non-UI code (data processing, validation, API service layer, state management logic) resides in `/shared`.
2. **UI Components**: 
   - Primitive UI components (buttons, inputs, cards) are built in `/ui` using a styling abstraction that adapts to web and mobile.
   - Platform-specific UI (e.g., modals, navigation headers) may have web/mobile variants in `/ui` with shared logic.
3. **Hooks**: Custom hooks (data fetching, form handling, offline detection) are in `/shared` and used by both web and mobile.
4. **Assets**: Images, icons, and fonts are stored in `/shared/assets` with platform-appropriate usage.

## Navigation
- **Web**: React Router v6 for declarative routing, nested routes, and lazy loading.
- **Mobile**: React Navigation (Stack, Tab, Drawer navigators) with screen options and deep linking support.
- **Abstraction**: A shared navigation helper (`/shared/navigation`) provides a unified interface for common actions (navigate, goBack, reset) while delegating to platform-specific implementations.

## State Management
- **Global State**: Zustand for lightweight, scalable state management with middleware support (persist, logger). Works identically in web and mobile.
- **Server State**: React Query (TanStack Query) for caching, background updates, and stale-while-revalidate validation. Shared hooks in `/shared/query` encapsulate API endpoints.
- **Form State**: React Hook Form with resolver integration (Zod/Yup) for shared validation logic.
- **Persistence**: Zustand middleware persists state to localStorage (web) and AsyncStorage (mobile) via a shared adapter.

## API Service Layer
- **Axios Instance**: Configured in `/shared/api/client` with base URL, interceptors (authentication, error logging, retry logic), and timeout settings.
- **Endpoint Definitions**: RESTful API functions in `/shared/api/endpoints` return Axios promises.
- **React Query Integration**: Custom hooks in `/shared/query` wrap endpoints with caching, pagination, and mutation helpers.
- **Offline Queue**: Optional offline request queueing using a shared service that stores failed requests and replays on reconnection.

## Responsive Layouts
- **Styling Approach**: 
  - Web: CSS modules or Tailwind CSS for utility-first responsive design.
  - Mobile: Styled Components with platform-aware media queries (using `useWindowDimensions` from React Native) or a shared theme object.
- **Breakpoints**: Shared breakpoint definitions (sm, md, lg, xl) in `/shared/theme` used by both platforms.
- **Layout Components**: 
  - `Container`, `Row`, `Column` in `/ui/layout` adapt flexbox properties based on screen size.
  - Platform-specific adjustments (e.g., touch targets, font sizes) handled via props or theme.

## Offline Capabilities
- **Detection**: Shared `useOnline` hook (`/shared/hooks`) monitors navigator.onLine (web) and NetInfo (mobile) via platform-specific implementation.
- **Data Persistence**: 
  - React Query persists query cache to storage (via persistClient) for offline reads.
  - User-generated actions (forms, mutations) are queued in a shared offline store and synchronized on reconnect.
- **UI Feedback**: Shared components (`/ui/OfflineIndicator`, `/ui/SyncStatus`) display connectivity and sync status.
- **Conflict Resolution**: Timestamp-based or shared logic for resolving conflicts when syncing offline changes.

## Development Workflow
- **Monorepo Tooling**: Nx or Turborepo for caching, parallel execution, and affected commands.
- **Environment Variables**: Shared `.env` files with platform-specific overrides (e.g., API URLs).
- **Testing**: 
  - Unit tests: Jest with React Testing Library (web) and Jest with React Native Testing Library (mobile).
  - E2E: Cypress (web) and Detox (mobile) for critical user flows.
- **Linting/Formatting**: Shared ESLint, Prettier, and TypeScript configurations.

## Deployment
- **Web**: Static build (Vite/Webpack) deployed to CDN or static hosting.
- **Mobile**: 
  - Android: Gradle build producing AAP/APK.
  - iOS: Xcode build producing IPA.
  - Over-the-air updates via Expo (if managed) or CodePush (if bare).

## Conclusion
This architecture ensures a cohesive user experience across platforms while optimizing development efficiency through maximal code sharing. Key decisions—Zustand for state, React Query for server state, shared API layer, and adaptive UI—provide a scalable foundation for SENTINEL PRIME's evolution.