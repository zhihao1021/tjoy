from .article import Article, ArticleModel
from .article_history import ArticleHistory, ArticleHistoryModel
from .category import Category, CategoryModel
from .comment import Comment, CommentModel
from .conversation import Conversation, ConversationModel
from .message import Message, MessageModel
from .search_history import SearchHistory, SearchHistoryModel
from .user import User, UserModel

Article.model_rebuild()
ArticleHistory.model_rebuild()
Category.model_rebuild()
Comment.model_rebuild()
Conversation.model_rebuild()
Message.model_rebuild()
SearchHistory.model_rebuild()
User.model_rebuild()
