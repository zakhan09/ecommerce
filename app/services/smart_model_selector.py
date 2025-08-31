import re
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import httpx
from app.core.config import Settings


class SmartModelSelector:
    """
    Automatically selects the latest and best models from each AI provider
    IMPROVED VERSION with better latest model detection
    """

    # Model scoring patterns - higher priority = better
    OPENAI_SCORING = {
        'gpt-4o': {'priority': 1, 'category': 'latest', 'cost_tier': 'premium'},
        'gpt-4-turbo': {'priority': 2, 'category': 'advanced', 'cost_tier': 'premium'},
        'gpt-4': {'priority': 3, 'category': 'standard', 'cost_tier': 'premium'},
        'gpt-3.5-turbo': {'priority': 4, 'category': 'fast', 'cost_tier': 'budget'}
    }

    GEMINI_SCORING = {
        'gemini-1.5-pro': {'priority': 1, 'category': 'latest', 'cost_tier': 'premium'},
        'gemini-1.5-flash': {'priority': 2, 'category': 'fast', 'cost_tier': 'standard'},
        'gemini-pro': {'priority': 3, 'category': 'standard', 'cost_tier': 'budget'},
        'gemini-1.0-pro': {'priority': 4, 'category': 'standard', 'cost_tier': 'budget'}
    }

    # Claude models need special handling due to date versions
    CLAUDE_BASE_PATTERNS = {
        'claude-3-5-sonnet': {'priority': 1, 'category': 'latest', 'cost_tier': 'premium'},
        'claude-3-opus': {'priority': 2, 'category': 'advanced', 'cost_tier': 'premium'},
        'claude-3-sonnet': {'priority': 3, 'category': 'standard', 'cost_tier': 'standard'},
        'claude-3-haiku': {'priority': 4, 'category': 'fast', 'cost_tier': 'budget'}
    }

    @classmethod
    def extract_model_date(cls, model_id: str) -> Optional[datetime]:
        """
        Extract date from model IDs like:
        - 'claude-3-5-sonnet-20240620'
        - 'gpt-4o-mini-2024-07-18'
        - 'gpt-4.1-mini-2025-04-14'
        """
        # Pattern for YYYY-MM-DD (OpenAI style)
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', model_id)
        if date_match:
            try:
                year, month, day = date_match.groups()
                return datetime(int(year), int(month), int(day))
            except ValueError:
                pass

        # Pattern for YYYYMMDD (Claude style)
        date_match = re.search(r'(\d{8})$', model_id)
        if date_match:
            try:
                return datetime.strptime(date_match.group(1), '%Y%m%d')
            except ValueError:
                pass

        # Pattern for version numbers like 4.1 (treat as newer)
        version_match = re.search(r'gpt-(\d+)\.(\d+)', model_id)
        if version_match:
            major, minor = version_match.groups()
            # Treat version as pseudo-date (higher version = more recent)
            base_date = datetime(2024, 1, 1)
            return base_date + timedelta(days=int(major) * 365 + int(minor) * 30)

        return None

    @classmethod
    def is_latest_version(cls, model_id: str) -> bool:
        """
        Check if model is marked as 'latest' or is very recent
        """
        if 'latest' in model_id.lower():
            return True

        model_date = cls.extract_model_date(model_id)
        if model_date:
            # Consider models from last 6 months as "latest"
            cutoff_date = datetime.now() - timedelta(days=180)
            return model_date >= cutoff_date

        # Special cases for known latest models
        latest_indicators = [
            'gpt-4o',  # Latest OpenAI
            'gpt-4.1',  # Even newer OpenAI
            'claude-3-5',  # Latest Claude
            'gemini-1.5'  # Latest Gemini
        ]

        return any(indicator in model_id.lower() for indicator in latest_indicators)

    @classmethod
    def score_openai_model(cls, model_id: str) -> Tuple[int, int, str, str]:
        """
        IMPROVED scoring with better latest detection
        Score OpenAI models: (priority, bonus_score, category, cost_tier)
        Lower priority number = higher priority
        """
        # Get base scoring
        for pattern, info in cls.OPENAI_SCORING.items():
            if pattern in model_id.lower():
                bonus = 0
                category = info['category']

                # IMPROVED: Date-based scoring
                model_date = cls.extract_model_date(model_id)
                if model_date:
                    days_old = (datetime.now() - model_date).days
                    if days_old < 30:  # Very recent
                        bonus += 25
                        category = 'latest'
                    elif days_old < 90:  # Recent
                        bonus += 20
                    elif days_old < 180:  # Somewhat recent
                        bonus += 15

                # Bonus for 'mini' versions (cost-effective)
                if 'mini' in model_id:
                    bonus += 10

                # IMPROVED: Version-based bonuses
                if 'gpt-4.1' in model_id:  # Newest version
                    bonus += 30
                    category = 'latest'
                elif 'gpt-4o' in model_id:  # Current latest
                    bonus += 20

                # Bonus for 'latest' keyword
                if cls.is_latest_version(model_id):
                    bonus += 15

                return (
                    info['priority'],
                    bonus,
                    category,
                    info['cost_tier']
                )

        return (99, 0, 'unknown', 'unknown')

    @classmethod
    def score_gemini_model(cls, model_id: str) -> Tuple[int, int, str, str]:
        """IMPROVED Gemini scoring with latest detection"""
        for pattern, info in cls.GEMINI_SCORING.items():
            if pattern in model_id.lower():
                bonus = 0
                category = info['category']

                # Big bonus for 'latest' versions
                if 'latest' in model_id:
                    bonus += 25
                    category = 'latest'

                # Bonus for newer versions
                if '1.5' in model_id:
                    bonus += 15
                elif '2.0' in model_id:  # Future proofing
                    bonus += 30
                    category = 'latest'

                # Bonus for 'flash' (faster/cheaper)
                if 'flash' in model_id:
                    bonus += 8

                return (
                    info['priority'],
                    bonus,
                    category,
                    info['cost_tier']
                )

        return (99, 0, 'unknown', 'unknown')

    @classmethod
    def score_claude_model(cls, model_id: str) -> Tuple[int, int, str, str]:
        """IMPROVED Claude scoring with better date handling"""
        for pattern, info in cls.CLAUDE_BASE_PATTERNS.items():
            if pattern in model_id.lower():
                bonus = 0
                category = info['category']

                # IMPROVED: Parse date for recency bonus
                model_date = cls.extract_model_date(model_id)
                if model_date:
                    days_old = (datetime.now() - model_date).days
                    if days_old < 30:  # Very recent
                        bonus += 30
                        category = 'latest'
                    elif days_old < 90:  # Recent
                        bonus += 25
                    elif days_old < 180:  # Somewhat recent
                        bonus += 20
                    elif days_old < 365:  # Within a year
                        bonus += 10

                # Special handling for 3.5 models (always latest tier)
                if '3-5' in model_id or '3.5' in model_id:
                    bonus += 25
                    category = 'latest'

                return (
                    info['priority'],
                    bonus,
                    category,
                    info['cost_tier']
                )

        return (99, 0, 'unknown', 'unknown')

    @classmethod
    def ensure_model_diversity(cls, sorted_models: List[Dict], max_count: int) -> List[Dict]:
        """
        IMPROVED diversity ensuring we get mix of latest + efficient models
        """
        if not sorted_models:
            return []

        selected = []

        # STEP 1: Always include the absolute best model
        if sorted_models:
            selected.append(sorted_models[0])

        # STEP 2: Ensure category diversity (latest, fast, advanced)
        categories_seen = {sorted_models[0]['category']}

        for model in sorted_models[1:]:
            if len(selected) >= max_count:
                break

            model_category = model['category']

            # Prefer models from different categories
            if model_category not in categories_seen:
                selected.append(model)
                categories_seen.add(model_category)

        # STEP 3: Fill remaining slots with highest-scoring models
        for model in sorted_models:
            if len(selected) >= max_count:
                break
            if model not in selected:
                selected.append(model)

        return selected[:max_count]

    @classmethod
    async def get_curated_models(cls, settings: Settings, max_per_provider: int = 2) -> Dict[str, List[Dict]]:
        """
        MAIN METHOD: Get automatically curated best models from each provider
        IMPROVED with better error handling and fallbacks
        """
        curated = {
            'openai': [],
            'anthropic': [],
            'google': []
        }

        async with httpx.AsyncClient(timeout=15.0) as client:  # Increased timeout

            # === OpenAI Model Curation ===
            if settings.OPENAI_API_KEY:
                try:
                    print("🔍 Fetching OpenAI models...")
                    response = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
                    )
                    response.raise_for_status()
                    all_openai = response.json().get('data', [])

                    # Score and filter OpenAI models
                    scored_openai = []
                    for model in all_openai:
                        model_id = model['id']
                        if not model_id.startswith('gpt'):
                            continue

                        priority, bonus, category, cost_tier = cls.score_openai_model(model_id)

                        # Only include models we recognize
                        if priority < 99:
                            scored_openai.append({
                                'id': model_id,
                                'name': cls.format_openai_name(model_id),
                                'provider': 'openai',
                                'category': category,
                                'cost_tier': cost_tier,
                                'score': priority - bonus,  # Lower = better
                                'recommended': category == 'latest' or cls.is_latest_version(model_id),
                                'available': True
                            })

                    # Select best models with diversity
                    curated['openai'] = cls.ensure_model_diversity(
                        sorted(scored_openai, key=lambda x: x['score']),
                        max_per_provider
                    )

                    print(f"✅ Selected OpenAI models: {[m['id'] for m in curated['openai']]}")

                except Exception as e:
                    print(f"❌ OpenAI model curation failed: {e}")
                    # Add fallback models
                    curated['openai'] = cls._get_fallback_openai_models()[:max_per_provider]

            # === Gemini Model Curation ===
            if settings.GOOGLE_API_KEY:
                try:
                    print("🔍 Fetching Gemini models...")
                    response = await client.get(
                        f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.GOOGLE_API_KEY}"
                    )
                    response.raise_for_status()
                    all_gemini = response.json().get('models', [])

                    scored_gemini = []
                    for model in all_gemini:
                        if 'generateContent' not in model.get('supportedGenerationMethods', []):
                            continue

                        # Remove 'models/' prefix if present
                        model_id = model['name'].replace('models/', '')
                        if not 'gemini' in model_id.lower():
                            continue

                        priority, bonus, category, cost_tier = cls.score_gemini_model(model_id)

                        if priority < 99:
                            scored_gemini.append({
                                'id': model_id,
                                'name': cls.format_gemini_name(model_id),
                                'provider': 'google',
                                'category': category,
                                'cost_tier': cost_tier,
                                'score': priority - bonus,
                                'recommended': cls.is_latest_version(model_id) or category == 'latest',
                                'available': True
                            })

                    # Ensure fallback if no models found
                    if not scored_gemini:
                        scored_gemini = cls._get_fallback_gemini_models()

                    curated['google'] = cls.ensure_model_diversity(
                        sorted(scored_gemini, key=lambda x: x['score']),
                        max_per_provider
                    )

                    print(f"✅ Selected Gemini models: {[m['id'] for m in curated['google']]}")

                except Exception as e:
                    print(f"❌ Gemini model curation failed: {e}")
                    curated['google'] = cls._get_fallback_gemini_models()[:max_per_provider]

            # === Claude Model Curation ===
            if settings.ANTHROPIC_API_KEY:
                print("🔍 Curating Claude models...")
                # Use known Claude models since Anthropic doesn't have public endpoint
                claude_candidates = [
                    'claude-3-5-sonnet-20240620',  # Latest
                    'claude-3-5-haiku-20241022',  # Latest fast
                    'claude-3-opus-20240229',  # Most powerful
                    'claude-3-sonnet-20240229',  # Balanced
                    'claude-3-haiku-20240307'  # Fast
                ]

                scored_claude = []
                for model_id in claude_candidates:
                    priority, bonus, category, cost_tier = cls.score_claude_model(model_id)

                    scored_claude.append({
                        'id': model_id,
                        'name': cls.format_claude_name(model_id),
                        'provider': 'anthropic',
                        'category': category,
                        'cost_tier': cost_tier,
                        'score': priority - bonus,
                        'recommended': cls.is_latest_version(model_id) or category == 'latest',
                        'available': True
                    })

                curated['anthropic'] = cls.ensure_model_diversity(
                    sorted(scored_claude, key=lambda x: x['score']),
                    max_per_provider
                )

                print(f"✅ Selected Claude models: {[m['id'] for m in curated['anthropic']]}")

        # Debug output
        for provider, models in curated.items():
            if models:
                print(f"🎯 {provider.title()}: {len(models)} models selected")
                for model in models:
                    print(f"   - {model['id']} (score: {model['score']}, {model['category']})")

        return curated

    # === HELPER METHODS ===

    @classmethod
    def _get_fallback_openai_models(cls) -> List[Dict]:
        """Fallback OpenAI models with real, latest IDs"""
        return [
            {
                'id': 'gpt-4o-mini',
                'name': 'GPT-4o Mini',
                'provider': 'openai',
                'category': 'latest',
                'cost_tier': 'premium',
                'score': -15,
                'recommended': True,
                'available': True
            },
            {
                'id': 'gpt-4o',
                'name': 'GPT-4o',
                'provider': 'openai',
                'category': 'latest',
                'cost_tier': 'premium',
                'score': -10,
                'recommended': True,
                'available': True
            }
        ]

    @classmethod
    def _get_fallback_gemini_models(cls) -> List[Dict]:
        """Fallback Gemini models"""
        return [
            {
                'id': 'gemini-1.5-pro-latest',
                'name': 'Gemini 1.5 Pro',
                'provider': 'google',
                'category': 'latest',
                'cost_tier': 'premium',
                'score': -14,
                'recommended': True,
                'available': True
            },
            {
                'id': 'gemini-1.5-flash-latest',
                'name': 'Gemini 1.5 Flash',
                'provider': 'google',
                'category': 'fast',
                'cost_tier': 'standard',
                'score': -21,
                'recommended': True,
                'available': True
            }
        ]

    # === FORMATTING METHODS (keep existing) ===

    @classmethod
    def format_openai_name(cls, model_id: str) -> str:
        """Format OpenAI model ID to user-friendly name"""
        if 'gpt-4o-mini' in model_id:
            return 'GPT-4o Mini'
        elif 'gpt-4.1' in model_id:
            return 'GPT-4.1'  # NEW: Handle GPT-4.1
        elif 'gpt-4o' in model_id:
            return 'GPT-4o'
        elif 'gpt-4-turbo' in model_id:
            return 'GPT-4 Turbo'
        elif 'gpt-4' in model_id:
            return 'GPT-4'
        elif 'gpt-3.5' in model_id:
            return 'GPT-3.5 Turbo'

        # Fallback: clean up the ID
        name = model_id.upper().replace('-', ' ')
        return name.title()

    @classmethod
    def format_gemini_name(cls, model_id: str) -> str:
        """Format Gemini model ID to user-friendly name"""
        if 'gemini-1.5-pro' in model_id:
            return 'Gemini 1.5 Pro'
        elif 'gemini-1.5-flash' in model_id:
            return 'Gemini 1.5 Flash'
        elif 'gemini-pro' in model_id:
            return 'Gemini Pro'
        return model_id.replace('-', ' ').title()

    @classmethod
    def format_claude_name(cls, model_id: str) -> str:
        """Format Claude model ID to user-friendly name"""
        if 'claude-3-5-sonnet' in model_id:
            return 'Claude 3.5 Sonnet'
        elif 'claude-3-5-haiku' in model_id:
            return 'Claude 3.5 Haiku'
        elif 'claude-3-opus' in model_id:
            return 'Claude 3 Opus'
        elif 'claude-3-sonnet' in model_id:
            return 'Claude 3 Sonnet'
        elif 'claude-3-haiku' in model_id:
            return 'Claude 3 Haiku'
        return model_id.replace('-', ' ').title()

    @classmethod
    async def get_recommended_defaults(cls, settings: Settings) -> Dict[str, str]:
        """
        Get the single best recommended model from each provider
        """
        curated = await cls.get_curated_models(settings, max_per_provider=1)

        defaults = {}
        if curated['openai']:
            defaults['openai'] = curated['openai'][0]['id']
        if curated['google']:
            defaults['google'] = curated['google'][0]['id']
        if curated['anthropic']:
            defaults['anthropic'] = curated['anthropic'][0]['id']

        return defaults