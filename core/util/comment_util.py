from typing import List

from core.domain.feed.feed_model import Feed
from core.domain.user.user_model import User
from core.dto.comment_dto import CommentResponse, CommentDto


class CommentBuilder:
    @staticmethod
    def layering(
        login_user_id: int, comments: List[CommentDto]
    ) -> List[CommentResponse]:
        parent_comments: List[CommentDto] = [
            comment for comment in comments if comment.parent_comment is None
        ]

        parent_to_children = CommentBuilder._parent_to_children_dict(
            comments, parent_comments
        )

        result = []

        for parent_comment in parent_comments:
            parent_id = parent_comment.id
            children = parent_to_children[parent_id]
            children_comments = CommentBuilder._build_children(children, login_user_id)
            parent_comment_feed = Feed.get_or_raise(parent_comment.feed)
            is_writer = (
                User.get_or_raise(parent_comment.user) == parent_comment_feed.user
            )

            parent_comment_response = CommentResponse.of_dto(
                comment=parent_comment,
                children_comments=children_comments,
                is_writer=is_writer,
            )

            result.append(parent_comment_response)

        return result

    @staticmethod
    def _parent_to_children_dict(
        comments: List[CommentDto], parent_comments: List[CommentDto]
    ) -> dict:
        parent_to_children = {comment.id: [] for comment in parent_comments}

        for comment in comments:
            if comment.parent_comment is not None:
                parent_to_children[comment.parent_comment].append(comment)

        return parent_to_children

    @staticmethod
    def _build_children(
        children: List[CommentDto], login_user_id: int
    ) -> List[CommentResponse]:
        children_comments = []

        for child in children:
            child_feed = Feed.get_or_raise(child.feed)
            is_writer = User.get_or_raise(child.user) == child_feed.user
            child_comment = CommentResponse.of_dto(comment=child, is_writer=is_writer)
            children_comments.append(child_comment)

        children_comments.sort(key=lambda comment: comment.created_at)

        return children_comments
