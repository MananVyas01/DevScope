"""
Productivity Classification Prompt Templates

This file contains prompt templates for different types of commit analysis
to improve classification accuracy and consistency.
"""

# Base system prompt for the AI assistant
SYSTEM_PROMPT = """You are an expert software development productivity analyst with deep understanding of:

1. Developer workflow patterns and productivity indicators
2. Code change analysis and intent recognition  
3. Git commit message conventions and semantics
4. Software development lifecycle phases
5. Common programming patterns and refactoring techniques

Your task is to analyze Git commits and classify developer productivity contexts with high accuracy.
Always respond with valid JSON following the specified format exactly."""

# Main analysis prompt template
ANALYSIS_PROMPT_TEMPLATE = """Analyze this Git commit and classify the developer's productivity context.

COMMIT INFORMATION:
- Message: "{message}"
- Files changed: {file_list}
- Statistics: +{additions} additions, -{deletions} deletions, {files_changed} files
- Detected type: {commit_type}
- Branch: {branch}
- Is merge commit: {is_merge}

CODE CHANGES:
{diff_content}

CLASSIFICATION TASK:
Based on the commit message, code changes, and diff patterns, classify this commit into ONE of these productivity contexts:

- High Focus: Deep, concentrated work with significant meaningful changes
- Distracted: Frequent small changes, unclear intent, scattered modifications
- Refactoring: Code restructuring without changing functionality
- Bug Fixing: Targeted fixes for specific issues or errors
- Research Spike: Experimental changes, trying different approaches
- Feature Development: Building new functionality or capabilities
- Testing: Adding, modifying, or fixing tests
- Documentation: Updating docs, comments, or README files
- Code Review: Changes made in response to review feedback
- Setup/Configuration: Project setup, config changes, dependency updates

ANALYSIS FACTORS:
1. Commit message clarity and intent
2. Code change patterns (additions vs deletions vs modifications)
3. File types and locations modified
4. Size and scope of changes
5. Whether changes suggest focused vs exploratory work
6. Consistency and coherence of changes

RESPONSE FORMAT (JSON only):
{{
  "label": "exact productivity label from list above",
  "confidence": 0.85,
  "reasoning": "concise explanation of classification decision",
  "indicators": ["key", "factors", "that", "influenced", "decision"]
}}"""

# Specialized prompts for different scenarios
MERGE_COMMIT_PROMPT = """This is a merge commit. Analyze the merge context:

MERGE INFORMATION:
- Message: "{message}"
- Branch: {branch}
- Files affected: {files_changed}

For merge commits, focus on:
- Was this a routine merge or complex conflict resolution?
- Does the merge represent feature completion or maintenance?
- Are there conflict resolution indicators?

Classify as appropriate productivity context, considering merge commits typically represent:
- Feature Development (if completing a feature branch)
- Code Review (if merging after review process)
- Setup/Configuration (if merging config/infrastructure changes)
- High Focus (if significant manual conflict resolution was required)"""

LARGE_COMMIT_PROMPT = """This is a large commit with {files_changed} files and {total_changes} changes.

Large commits often indicate:
- Initial project setup
- Major refactoring efforts
- Feature branch squashing
- Auto-generated changes

Analyze the scale and nature of changes to determine if this represents:
- High Focus: Sustained development effort
- Refactoring: Large-scale code restructuring
- Setup/Configuration: Initial setup or major infrastructure changes
- Feature Development: Comprehensive feature implementation"""

SMALL_COMMIT_PROMPT = """This is a small commit with minimal changes ({total_changes} total changes).

Small commits can indicate:
- Focused, incremental development
- Quick bug fixes
- Minor adjustments or tweaks
- Distracted or interrupted work

Analyze the precision and intent of the changes."""

# Language/framework specific analysis hints
LANGUAGE_ANALYSIS_HINTS = {
    'javascript': {
        'test_patterns': ['test', 'spec', '__tests__', '.test.', '.spec.'],
        'config_patterns': ['package.json', 'webpack', 'babel', 'eslint', 'tsconfig'],
        'setup_patterns': ['node_modules', 'yarn.lock', 'package-lock.json']
    },
    'python': {
        'test_patterns': ['test_', '_test.py', 'tests/', 'pytest'],
        'config_patterns': ['requirements.txt', 'setup.py', 'pyproject.toml', 'tox.ini'],
        'setup_patterns': ['__init__.py', 'setup.py', 'requirements']
    },
    'typescript': {
        'test_patterns': ['test', 'spec', '__tests__', '.test.', '.spec.'],
        'config_patterns': ['tsconfig.json', 'webpack', 'jest.config'],
        'setup_patterns': ['package.json', 'yarn.lock', 'node_modules']
    }
}

# Confidence level guidelines
CONFIDENCE_GUIDELINES = """
CONFIDENCE SCORING GUIDELINES:

0.9-1.0 (Very High):
- Clear, unambiguous commit message
- Consistent code changes matching message intent
- Strong pattern indicators (e.g., "fix" + error handling changes)

0.7-0.8 (High):
- Good commit message with mostly consistent changes
- Some clear indicators but minor ambiguity

0.5-0.6 (Medium):
- Unclear commit message or mixed change patterns
- Some conflicting indicators
- Moderate uncertainty in classification

0.3-0.4 (Low):
- Ambiguous or missing commit message
- Scattered or inconsistent changes
- Multiple possible classifications

0.1-0.2 (Very Low):
- Completely unclear intent
- Random or auto-generated changes
- High uncertainty in classification
"""

def get_analysis_prompt(commit_data: dict) -> str:
    """
    Generate the appropriate analysis prompt based on commit characteristics.
    
    Args:
        commit_data: Dictionary containing commit information
        
    Returns:
        Formatted prompt string
    """
    # Extract data
    message = commit_data.get('message', '')
    files_changed = commit_data.get('files_changed', [])
    stats = commit_data.get('stats', {})
    diff_content = commit_data.get('diff', '')
    commit_type = commit_data.get('commit_type', 'other')
    branch = commit_data.get('branch', 'unknown')
    is_merge = commit_data.get('is_merge', False)
    
    # Prepare file list
    file_list = ', '.join([f['path'] for f in files_changed[:10]])
    if len(files_changed) > 10:
        file_list += f" ... and {len(files_changed) - 10} more files"
    
    # Truncate diff if too long
    if len(diff_content) > 3000:
        diff_content = diff_content[:3000] + "\n... (truncated for analysis)"
    
    # Choose appropriate prompt based on commit characteristics
    total_changes = stats.get('additions', 0) + stats.get('deletions', 0)
    
    if is_merge:
        # Use merge-specific prompt
        base_prompt = MERGE_COMMIT_PROMPT
    elif len(files_changed) > 20 or total_changes > 500:
        # Use large commit prompt
        base_prompt = LARGE_COMMIT_PROMPT
    elif total_changes < 10:
        # Use small commit prompt  
        base_prompt = SMALL_COMMIT_PROMPT
    else:
        # Use standard prompt
        base_prompt = ANALYSIS_PROMPT_TEMPLATE
    
    # Format the prompt
    return base_prompt.format(
        message=message,
        file_list=file_list,
        additions=stats.get('additions', 0),
        deletions=stats.get('deletions', 0),
        files_changed=len(files_changed),
        commit_type=commit_type,
        branch=branch,
        is_merge=is_merge,
        diff_content=diff_content,
        total_changes=total_changes
    )

def get_system_prompt() -> str:
    """Get the system prompt for the AI assistant."""
    return SYSTEM_PROMPT

def analyze_file_patterns(files_changed: list) -> dict:
    """
    Analyze file patterns to provide additional context hints.
    
    Args:
        files_changed: List of file change dictionaries
        
    Returns:
        Dictionary with pattern analysis
    """
    patterns = {
        'test_files': 0,
        'config_files': 0,
        'setup_files': 0,
        'languages': set(),
        'file_types': set()
    }
    
    for file_change in files_changed:
        path = file_change.get('path', '').lower()
        
        # Detect language
        if path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            patterns['languages'].add('javascript')
        elif path.endswith('.py'):
            patterns['languages'].add('python')
        elif path.endswith('.java'):
            patterns['languages'].add('java')
        elif path.endswith(('.cpp', '.c', '.h')):
            patterns['languages'].add('c++')
        
        # Detect file types
        if '.' in path:
            ext = path.split('.')[-1]
            patterns['file_types'].add(ext)
        
        # Detect patterns
        if any(pattern in path for pattern in ['test', 'spec', '__tests__']):
            patterns['test_files'] += 1
        elif any(pattern in path for pattern in ['config', 'package.json', 'requirements', 'setup']):
            patterns['config_files'] += 1
        elif any(pattern in path for pattern in ['__init__', 'main', 'index']):
            patterns['setup_files'] += 1
    
    return patterns
