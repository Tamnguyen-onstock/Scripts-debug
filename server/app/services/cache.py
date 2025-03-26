import hashlib
import time
import json
import logging
from typing import Dict, Any, Optional
from app.core.settings import settings

# Initialize logger
logger = logging.getLogger("mcp_intent_server")

class QueryCache:
    """Cache for storing analysis results for queries."""
    
    def __init__(self, ttl=settings.CACHE_TTL, max_size=settings.MAX_CACHE_SIZE):
        """
        Initialize the cache.
        
        Args:
            ttl: Time-to-live for cache entries (seconds)
            max_size: Maximum number of entries in the cache
        """
        self.cache = {}
        self.ttl = ttl
        self.max_size = max_size
        self.expiry = {}  # Expiry time for each key
        self.access_times = {}  # Last access time for each key
        
    def _generate_key(self, tool_name: str, query: str) -> str:
        """Generate a cache key from tool name and query."""
        # Create a unique key by hashing the tool name and query
        key_string = f"{tool_name}:{query.lower().strip()}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def get(self, tool_name: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Get a result from the cache if it exists and is not expired.
        
        Args:
            tool_name: Name of the tool being called
            query: User query
            
        Returns:
            Optional[Dict[str, Any]]: Result from cache or None if not found
        """
        if not settings.CACHE_ENABLED:
            return None
            
        key = self._generate_key(tool_name, query)
        
        # Check if key is in cache
        if key not in self.cache:
            return None
            
        # Check if cache is expired
        now = time.time()
        if now > self.expiry.get(key, 0):
            # Remove expired cache
            self._remove(key)
            return None
            
        # Update access time
        self.access_times[key] = now
        
        logger.info(f"Cache hit for tool '{tool_name}' and query: {query}")
        return self.cache[key]
    
    def set(self, tool_name: str, query: str, result: Dict[str, Any]) -> None:
        """
        Store a result in the cache.
        
        Args:
            tool_name: Name of the tool being called
            query: User query
            result: Result to cache
        """
        if not settings.CACHE_ENABLED:
            return
            
        key = self._generate_key(tool_name, query)
        now = time.time()
        
        # Check if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Evict least recently accessed entry
            self._evict_oldest()
        
        # Store result in cache
        self.cache[key] = result
        self.expiry[key] = now + self.ttl
        self.access_times[key] = now
        
        logger.info(f"Cached result for tool '{tool_name}' and query: {query}")
    
    def _remove(self, key: str) -> None:
        """Remove an entry from the cache."""
        if key in self.cache:
            del self.cache[key]
        if key in self.expiry:
            del self.expiry[key]
        if key in self.access_times:
            del self.access_times[key]
    
    def _evict_oldest(self) -> None:
        """Evict the least recently accessed entry from the cache."""
        if not self.access_times:
            return
            
        # Find the key with the oldest access time
        oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        self._remove(oldest_key)
    
    def clear(self) -> None:
        """Clear the entire cache."""
        self.cache.clear()
        self.expiry.clear()
        self.access_times.clear()
        
    def remove_expired(self) -> None:
        """Remove all expired entries."""
        now = time.time()
        expired_keys = [key for key, exp_time in self.expiry.items() if now > exp_time]
        
        for key in expired_keys:
            self._remove(key)
            
        if expired_keys:
            logger.info(f"Removed {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache."""
        return {
            "enabled": settings.CACHE_ENABLED,
            "ttl": self.ttl,
            "max_size": self.max_size,
            "current_size": len(self.cache),
            "memory_usage_estimate": sum(len(json.dumps(v)) for v in self.cache.values())
        }

# Initialize cache
query_cache = QueryCache()