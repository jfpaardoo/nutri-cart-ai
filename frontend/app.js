/**
 * ComeYCuadra - Frontend Entry Point (Decoupled Architecture)
 * 
 * The previous monolithic app.js has been decomposed into dedicated ES modules
 * following Single Responsibility Principle (SRP) and Clean Architecture:
 * 
 * - ./js/state.js     : Reactive state management, macro balancing & percentage calculation.
 * - ./js/api.js       : Asynchronous HTTP client communicating with backend endpoints.
 * - ./js/ui-render.js : Pure UI DOM rendering components (recipes, quantities, basket, metrics).
 * - ./js/main.js      : Application orchestrator, event delegation & window bindings.
 */

import "./js/main.js";
export * from "./js/state.js";
export * from "./js/api.js";
export * from "./js/ui-render.js";
export * from "./js/main.js";
