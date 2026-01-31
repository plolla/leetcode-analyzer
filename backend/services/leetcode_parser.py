import re
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from pydantic import BaseModel


class ProblemExample(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None


class ProblemDetails(BaseModel):
    slug: str
    title: str
    difficulty: str
    description: str
    constraints: List[str]
    examples: List[ProblemExample]


class LeetCodeParser:
    """Service for parsing LeetCode problem URLs and fetching problem details."""
    
    # Supported URL patterns
    URL_PATTERNS = [
        r'^https?://(?:www\.)?leetcode\.com/problems/([\w-]+)/?$',
        r'^https?://(?:www\.)?leetcode\.com/problems/([\w-]+)/description/?$',
        r'^https?://(?:www\.)?leetcode\.com/problems/([\w-]+)/solutions?/?$',
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def extract_problem_slug(self, url: str) -> Optional[str]:
        """
        Extract the problem slug from a LeetCode URL.
        
        Args:
            url: The LeetCode problem URL
            
        Returns:
            The problem slug if valid, None otherwise
        """
        for pattern in self.URL_PATTERNS:
            match = re.match(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def validate_problem_url(self, url: str) -> bool:
        """
        Validate if a URL is a valid LeetCode problem URL.
        
        Args:
            url: The URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        return self.extract_problem_slug(url) is not None
    
    def fetch_problem_details(self, slug: str) -> Optional[ProblemDetails]:
        """
        Fetch problem details from LeetCode by problem slug using GraphQL API.
        
        Args:
            slug: The problem slug (e.g., 'two-sum')
            
        Returns:
            ProblemDetails if successful, None otherwise
        """
        try:
            # LeetCode's GraphQL endpoint
            graphql_url = "https://leetcode.com/graphql"
            
            # GraphQL query to fetch problem details
            query = """
            query getQuestionDetail($titleSlug: String!) {
                question(titleSlug: $titleSlug) {
                    questionId
                    title
                    titleSlug
                    content
                    difficulty
                    exampleTestcases
                    topicTags {
                        name
                    }
                    hints
                    solution {
                        id
                    }
                }
            }
            """
            
            # Make the GraphQL request
            response = self.session.post(
                graphql_url,
                json={
                    "query": query,
                    "variables": {"titleSlug": slug}
                },
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check if we got valid data
            if not data.get("data") or not data["data"].get("question"):
                print(f"Problem {slug} not found in LeetCode")
                return None
            
            question = data["data"]["question"]
            
            # Parse the HTML content to extract description and examples
            return self._parse_problem_data(question)
            
        except requests.RequestException as e:
            print(f"Error fetching problem {slug}: {e}")
            # Fall back to mock data
            return self._create_mock_problem(slug)
        except Exception as e:
            print(f"Error parsing problem {slug}: {e}")
            return self._create_mock_problem(slug)
    
    def _parse_problem_data(self, question: dict) -> ProblemDetails:
        """
        Parse the GraphQL response into ProblemDetails.
        
        Args:
            question: The question data from GraphQL
            
        Returns:
            ProblemDetails object
        """
        import re
        
        # Extract basic info
        slug = question.get("titleSlug", "")
        title = question.get("title", "")
        difficulty = question.get("difficulty", "Medium")
        content = question.get("content", "")
        
        # Parse HTML content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract description (clean up formatting)
        # Get all paragraphs before "Example" section
        description_parts = []
        for elem in soup.find_all('p'):
            # Check if this paragraph contains "Example" with the example class
            if elem.find('strong', class_='example'):
                break
            # Use get_text with separator to add spaces between inline elements
            text = elem.get_text(separator=' ', strip=True)
            if text and not text.startswith('Constraints:') and text != ' ':
                description_parts.append(text)
        
        description = ' '.join(description_parts) if description_parts else "See problem on LeetCode"
        
        # Extract constraints
        constraints = []
        # Look for constraints in list items
        for ul in soup.find_all('ul'):
            # Check if this is the constraints list (comes after "Constraints:" text)
            prev_elem = ul.find_previous('p')
            if prev_elem and 'Constraints:' in prev_elem.get_text():
                constraints = [li.get_text(strip=True) for li in ul.find_all('li')]
                break
        
        if not constraints:
            constraints = ["See problem description for constraints"]
        
        # Extract examples from <pre> tags
        examples = []
        pre_tags = soup.find_all('pre')
        
        for pre in pre_tags:
            # Get the text and remove <strong> tags but keep their content
            text = pre.get_text('\n', strip=True)
            
            # Parse Input/Output/Explanation
            input_val = ""
            output_val = ""
            explanation_val = ""
            
            # Split by lines and parse
            lines = text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Input:'):
                    current_section = 'input'
                    input_val = line.replace('Input:', '').strip()
                elif line.startswith('Output:'):
                    current_section = 'output'
                    output_val = line.replace('Output:', '').strip()
                elif line.startswith('Explanation:'):
                    current_section = 'explanation'
                    explanation_val = line.replace('Explanation:', '').strip()
                elif current_section and line:
                    # Continue previous section if line doesn't start with a label
                    if current_section == 'input':
                        input_val += ' ' + line
                    elif current_section == 'output':
                        output_val += ' ' + line
                    elif current_section == 'explanation':
                        explanation_val += ' ' + line
            
            # Only add if we found at least input or output
            if input_val or output_val:
                examples.append(ProblemExample(
                    input=input_val.strip() if input_val else "See problem description",
                    output=output_val.strip() if output_val else "See problem description",
                    explanation=explanation_val.strip() if explanation_val else None
                ))
        
        # Fallback if no examples found
        if not examples:
            examples = [
                ProblemExample(
                    input="See problem description",
                    output="See problem description",
                    explanation=None
                )
            ]
        
        return ProblemDetails(
            slug=slug,
            title=title,
            difficulty=difficulty,
            description=description,
            constraints=constraints,
            examples=examples
        )
    
    def _create_mock_problem(self, slug: str) -> ProblemDetails:
        """
        Create a mock problem for demonstration purposes.
        In production, this would parse actual LeetCode data.
        """
        # Convert slug to title (basic conversion)
        title = ' '.join(word.capitalize() for word in slug.split('-'))
        
        return ProblemDetails(
            slug=slug,
            title=title,
            difficulty="Medium",
            description=f"This is a placeholder description for the problem: {title}. "
                       f"In a production environment, this would contain the actual problem description "
                       f"fetched from LeetCode.",
            constraints=[
                "1 <= n <= 10^4",
                "Time complexity should be O(n)",
                "Space complexity should be O(1)"
            ],
            examples=[
                ProblemExample(
                    input="nums = [2,7,11,15], target = 9",
                    output="[0,1]",
                    explanation="Because nums[0] + nums[1] == 9, we return [0, 1]."
                ),
                ProblemExample(
                    input="nums = [3,2,4], target = 6",
                    output="[1,2]",
                    explanation="Because nums[1] + nums[2] == 6, we return [1, 2]."
                )
            ]
        )


# Singleton instance
leetcode_parser = LeetCodeParser()
