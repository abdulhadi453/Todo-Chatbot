"""
Dependency injection patterns for the application.
This module provides a way to manage and inject dependencies across the application.
"""

from abc import ABC
from typing import Any, Dict, Type, TypeVar, Callable, Optional
from functools import wraps
import inspect


T = TypeVar('T')


class Injectable(ABC):
    """
    Base class for all injectable services.
    This class provides a way to identify injectable services.
    """
    pass


class Container:
    """
    Simple dependency injection container.
    This container manages the instantiation and lifetime of services.
    """

    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(self, service_class: Type[T], instance: T) -> None:
        """
        Register a service instance in the container.

        Args:
            service_class: The class of the service
            instance: The instance of the service
        """
        self._services[service_class] = instance

    def register_factory(self, service_class: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory function for a service class.

        Args:
            service_class: The class of the service
            factory: Factory function to create instances
        """
        self._factories[service_class] = factory

    def register_singleton(self, service_class: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a singleton service that will be instantiated once.

        Args:
            service_class: The class of the service
            factory: Factory function to create the singleton instance
        """
        # Instantiate the service immediately for singletons
        self._singletons[service_class] = factory()

    def resolve(self, service_class: Type[T]) -> T:
        """
        Resolve and return an instance of the requested service.

        Args:
            service_class: The class of the service to resolve

        Returns:
            Instance of the requested service
        """
        # Check for singleton first
        if service_class in self._singletons:
            return self._singletons[service_class]

        # Check for registered instance
        if service_class in self._services:
            return self._services[service_class]

        # Check for registered factory
        if service_class in self._factories:
            return self._factories[service_class]()

        # If not found, try to instantiate the class directly
        # This assumes the class has no required constructor parameters
        try:
            return service_class()
        except TypeError as e:
            # If the constructor requires parameters, raise an error
            raise ValueError(f"Service {service_class.__name__} not registered in container and could not be instantiated directly: {e}")

    def resolve_dependencies(self, func: Callable) -> Callable:
        """
        Decorator to automatically inject dependencies for a function.

        Args:
            func: The function to decorate

        Returns:
            Function with dependencies injected
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the function signature to determine parameter types
            sig = inspect.signature(func)

            # Resolve dependencies for parameters not provided
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()

            # Inject any missing dependencies
            for param_name, param in sig.parameters.items():
                if param_name not in bound_args.arguments:
                    # Try to resolve the parameter type
                    if hasattr(param.annotation, '__origin__'):
                        # Handle generic types
                        param_type = param.annotation.__origin__
                    else:
                        param_type = param.annotation

                    # Skip if annotation is empty (like 'Any' or 'object')
                    if param_type is not inspect.Parameter.empty and param_type != inspect.Parameter.empty:
                        try:
                            resolved_dep = self.resolve(param_type)
                            bound_args.arguments[param_name] = resolved_dep
                        except (ValueError, KeyError):
                            # If we can't resolve the dependency, skip it
                            # Let the function handle missing parameters
                            continue

            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper


# Global container instance
container = Container()


def register_service(service_class: Type[T]):
    """
    Decorator to register a service in the container.
    This decorator registers a service as a singleton.

    Args:
        service_class: The class to register as a service
    """
    # Register the class as a singleton with a default factory
    container.register_singleton(service_class, service_class)
    return service_class


def inject(func: Callable) -> Callable:
    """
    Decorator to inject dependencies into a function.

    Args:
        func: Function to inject dependencies into

    Returns:
        Function with dependencies injected
    """
    return container.resolve_dependencies(func)


def get_service(service_class: Type[T]) -> T:
    """
    Get a service instance from the container.

    Args:
        service_class: Class of the service to retrieve

    Returns:
        Instance of the requested service
    """
    return container.resolve(service_class)


# Pre-register some common services
def initialize_container():
    """
    Initialize the container with common services.
    This is called to set up default services.
    """
    # We could pre-register common services here if needed
    # For now, this is a placeholder for future initialization
    pass


# Initialize the container
initialize_container()