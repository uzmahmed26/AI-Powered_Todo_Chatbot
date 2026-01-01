"""
Skills Registry

Decorator-based skill registration system for reusable agent skills.
"""

from typing import Callable, Dict, Any, List, TypeVar, get_type_hints
from functools import wraps
import inspect

# Type variables for generic skill functions
T = TypeVar('T')
R = TypeVar('R')

# Global skill registry
SKILL_REGISTRY: Dict[str, Dict[str, Any]] = {}


def skill(name: str, version: str = "1.0.0"):
    """
    Decorator to register a function as an agent skill.

    Args:
        name: Unique skill identifier (e.g., "task_filtering")
        version: Semantic version (MAJOR.MINOR.PATCH, default: "1.0.0")

    Returns:
        Decorated function registered in SKILL_REGISTRY

    Example:
        @skill(name="task_filtering", version="1.0.0")
        def filter_tasks(tasks: List[Task], filters: FilterCriteria) -> List[Task]:
            '''Filter tasks by status, date, priority.'''
            return [t for t in tasks if meets_criteria(t, filters)]

        # Skill is now registered and can be invoked
        result = invoke_skill("task_filtering", tasks=[...], filters=...)
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        # Extract function metadata
        type_hints = get_type_hints(func)
        input_schema = {k: v for k, v in type_hints.items() if k != 'return'}
        output_schema = type_hints.get('return', Any)
        signature = inspect.signature(func)
        
        # Register skill with metadata
        skill_key = f"{name}:{version}"
        SKILL_REGISTRY[name] = {
            'name': name,
            'version': version,
            'function': func,
            'input_schema': input_schema,
            'output_schema': output_schema,
            'signature': signature,
            'description': func.__doc__ or "",
            'module': func.__module__,
        }
        
        # Also register with versioned key for version-specific lookups
        SKILL_REGISTRY[skill_key] = SKILL_REGISTRY[name]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapped function preserves original behavior"""
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def invoke_skill(name: str, version: str | None = None, **kwargs) -> Any:
    """
    Invoke a skill by name with keyword arguments.

    Args:
        name: Skill name
        version: Optional specific version (defaults to latest)
        **kwargs: Skill input parameters

    Returns:
        Skill output

    Raises:
        ValueError: If skill not found
        TypeError: If parameters don't match skill signature

    Example:
        result = invoke_skill(
            name="task_filtering",
            tasks=[...],
            filters=FilterCriteria(status=['pending'])
        )
    """
    # Determine lookup key
    lookup_key = f"{name}:{version}" if version else name
    
    if lookup_key not in SKILL_REGISTRY:
        available = list_available_skills()
        available_names = [s['name'] for s in available]
        raise ValueError(
            f"Skill '{lookup_key}' not found in registry. "
            f"Available skills: {', '.join(available_names)}"
        )
    
    skill_metadata = SKILL_REGISTRY[lookup_key]
    skill_func = skill_metadata['function']
    
    try:
        return skill_func(**kwargs)
    except TypeError as e:
        signature = skill_metadata['signature']
        raise TypeError(
            f"Skill '{name}' invocation failed: {e}. "
            f"Expected signature: {signature}"
        )


def list_available_skills() -> List[Dict[str, Any]]:
    """
    List all available skills with metadata.

    Returns:
        List of skill metadata dictionaries (without versioned duplicates)

    Example:
        skills = list_available_skills()
        for skill in skills:
            print(f"{skill['name']} v{skill['version']}: {skill['description']}")
    """
    # Filter out versioned duplicates (keep only base name entries)
    unique_skills = []
    seen_names = set()
    
    for key, metadata in SKILL_REGISTRY.items():
        # Skip versioned keys (contain ':')
        if ':' in key:
            continue
        
        name = metadata['name']
        if name not in seen_names:
            unique_skills.append({
                'name': metadata['name'],
                'version': metadata['version'],
                'description': metadata['description'].strip() if metadata['description'] else "",
                'input_schema': metadata['input_schema'],
                'output_schema': metadata['output_schema'],
                'module': metadata['module'],
            })
            seen_names.add(name)
    
    return sorted(unique_skills, key=lambda s: s['name'])


def get_skill_metadata(name: str, version: str | None = None) -> Dict[str, Any]:
    """
    Get metadata for a specific skill.

    Args:
        name: Skill name
        version: Optional specific version

    Returns:
        Skill metadata dictionary

    Raises:
        ValueError: If skill not found
    """
    lookup_key = f"{name}:{version}" if version else name

    if lookup_key not in SKILL_REGISTRY:
        raise ValueError(f"Skill '{lookup_key}' not found in registry")

    metadata = SKILL_REGISTRY[lookup_key].copy()
    # Remove function reference from returned metadata (not serializable)
    metadata.pop('function', None)

    return metadata


def get_registry() -> Dict[str, Dict[str, Any]]:
    """
    Get the global skill registry.

    Returns:
        The SKILL_REGISTRY dictionary

    Example:
        registry = get_registry()
        if 'task_filtering' in registry:
            skill = registry['task_filtering']
    """
    return SKILL_REGISTRY
