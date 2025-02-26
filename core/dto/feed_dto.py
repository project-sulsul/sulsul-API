from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from api.config.exceptions import BadRequestException
from core.domain.feed.feed_model import Feed
from core.dto.user_dto import UserSimpleInfoResponse
from core.util.cache import pairing_cache_store


class PairingDto(BaseModel):
    id: int
    name: str


class ClassificationResponse(BaseModel):
    foods: List[PairingDto]
    alcohols: List[PairingDto]


class FeedCreateRequest(BaseModel):
    title: str
    content: str
    represent_image: str
    images: List[str]
    alcohol_pairing_ids: List[int]
    food_pairing_ids: List[int]
    user_tags_raw_string: Optional[str]
    score: float

    def validate_input(self):
        if len(self.title) > 100:
            raise BadRequestException("제목은 100자 이하로 입력해주세요.")

        if len(self.content) > 500:
            raise BadRequestException("내용은 500자 이하로 입력해주세요.")

        if self.score < 0:
            raise BadRequestException("점수는 0 이상으로 입력해주세요.")

        for alcohol_id in self.alcohol_pairing_ids:
            try:
                pairing_cache_store.get_by_id(alcohol_id)
            except:
                raise BadRequestException(f"({alcohol_id}) 존재하지 않는 술 ID 입니다.")

        for food_id in self.food_pairing_ids:
            try:
                pairing_cache_store.get_by_id(food_id)
            except:
                raise BadRequestException(f"({food_id}) 존재하지 않는 안주 ID 입니다.")


class FeedResponse(BaseModel):
    feed_id: int
    writer_info: UserSimpleInfoResponse
    title: str
    content: str
    represent_image: str
    images: List[str]
    alcohol_pairing_ids: List[int]
    food_pairing_ids: List[int]
    alcohol_tags: List[str]
    food_tags: List[str]
    user_tags: Optional[List[str]]
    is_liked: bool = False
    view_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    score: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def of(cls, feed: Feed, likes_count: int, comments_count: int, is_liked: bool):
        return FeedResponse(
            **feed.__data__,
            feed_id=feed.id,
            writer_info=UserSimpleInfoResponse(
                user_id=feed.user.id, **feed.user.__data__
            ),
            alcohol_tags=pairing_cache_store.get_all_names_by_ids(
                feed.alcohol_pairing_ids
            ),
            food_tags=pairing_cache_store.get_all_names_by_ids(feed.food_pairing_ids),
            is_liked=is_liked,
            likes_count=likes_count,
            comments_count=comments_count,
        )

    @classmethod
    def from_orm(cls, feed: Feed):
        return FeedResponse(
            **feed.__data__,
            feed_id=feed.id,
            writer_info=UserSimpleInfoResponse(
                user_id=feed.user.id, **feed.user.__data__
            ),
            alcohol_tags=pairing_cache_store.get_all_names_by_ids(
                feed.alcohol_pairing_ids
            ),
            food_tags=pairing_cache_store.get_all_names_by_ids(feed.food_pairing_ids),
        )


class FeedUpdateRequest(BaseModel):
    title: Optional[str]
    content: Optional[str]
    images: Optional[List[str]]
    user_tags: Optional[List[str]]

    def validate_input(self):
        if len(self.title) > 100:
            raise BadRequestException("제목은 100자 이하로 입력해주세요.")

        if len(self.content) > 500:
            raise BadRequestException("내용은 500자 이하로 입력해주세요.")

        for alcohol_id in self.alcohol_pairing_ids:
            try:
                pairing_cache_store.get_by_id(alcohol_id)
            except:
                raise BadRequestException(f"({alcohol_id}) 존재하지 않는 술 ID 입니다.")

        for food_id in self.food_pairing_ids:
            try:
                pairing_cache_store.get_by_id(food_id)
            except:
                raise BadRequestException(f"({food_id}) 존재하지 않는 안주 ID 입니다.")


class FeedSearchResultResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]

    @classmethod
    def from_orm(cls, feed: Feed):
        return FeedSearchResultResponse(**feed.__data__)


class FeedSearchResultListResponse(BaseModel):
    keyword: str
    results: List[FeedSearchResultResponse]


class FeedSoftDeleteResponse(BaseModel):
    feed_id: int
    is_deleted: bool
    deleted_comments_count: int
    deleted_likes_count: int

    @classmethod
    def of(cls, feed: Feed, deleted_comments_count: int, deleted_likes_count: int):
        return FeedSoftDeleteResponse(
            feed_id=feed.id,
            is_deleted=feed.is_deleted,
            deleted_comments_count=deleted_comments_count,
            deleted_likes_count=deleted_likes_count,
        )


class RelatedFeedResponse(BaseModel):
    feed_id: int
    title: str
    represent_image: str
    score: float
    user_tags: Optional[List[str]]
    alcohol_tags: List[str]
    food_tags: List[str]
    is_liked: bool = False

    @classmethod
    def of(cls, feed: Feed, is_liked: bool):
        return RelatedFeedResponse(
            **feed.__data__,
            alcohol_tags=pairing_cache_store.get_all_names_by_ids(
                feed.alcohol_pairing_ids
            ),
            food_tags=pairing_cache_store.get_all_names_by_ids(feed.food_pairing_ids),
            feed_id=feed.id,
            is_liked=is_liked,
        )


class RandomFeedDto(BaseModel):
    feed_id: int
    title: str
    content: str
    represent_image: str
    user_id: int
    user_nickname: str
    user_image: Optional[str]
    comments_count: int
    likes_count: int
    updated_at: datetime
    is_liked: bool = False

    def __eq__(self, other):
        return self.feed_id == other.feed_id


class RandomFeedListResponse(BaseModel):
    ids_list: List[int]
    ids_string: str
    feeds: List["RandomFeedDto"]

    @classmethod
    def of_query_dto(cls, feeds: List["RandomFeedDto"]):
        return RandomFeedListResponse(
            ids_list=[feed.feed_id for feed in feeds],
            ids_string=",".join([str(feed.feed_id) for feed in feeds]),
            feeds=feeds,
        )


class PopularFeedDto(BaseModel):
    feed_id: int
    title: str
    content: str
    represent_image: str
    pairing_ids: List[int]
    images: List[str]
    like_count: int
    score: float
    user_id: int
    user_nickname: str
    user_image: Optional[str]
    created_at: datetime
    updated_at: datetime


class PopularFeedListDto(BaseModel):
    title: str
    feeds: List[PopularFeedDto] = []


class FeedByPreferenceResponse(BaseModel):
    feed_id: int
    title: str
    represent_image: str
    score: float
    alcohols: List[str]
    foods: List[str]
    writer_nickname: str

    @classmethod
    def of(cls, feed: Feed):
        from_cache = pairing_cache_store.get_all_names_by_ids
        return FeedByPreferenceResponse(
            feed_id=feed.id,
            alcohols=from_cache(feed.alcohol_pairing_ids),
            foods=from_cache(feed.food_pairing_ids),
            **feed.__data__,
            writer_nickname=feed.user.nickname,
        )


class FeedByPreferenceListResponse(BaseModel):
    feeds: List[FeedByPreferenceResponse] = []

    @classmethod
    def of(cls, feeds: List[Feed]):
        return FeedByPreferenceListResponse(
            feeds=sorted(
                [FeedByPreferenceResponse.of(feed) for feed in feeds],
                key=lambda x: x.score,
                reverse=True,
            ),
        )


class FeedByAlcoholResponse(BaseModel):
    subtype: str
    feed_id: int
    title: str
    represent_image: str
    foods: List[str]
    score: float
    writer_nickname: str

    @classmethod
    def of(cls, subtype: str, feed: Feed, foods: List[str]):
        return FeedByAlcoholResponse(
            subtype=subtype,
            feed_id=feed.id,
            foods=foods,
            **feed.__data__,
            writer_nickname=feed.user.nickname,
        )


class FeedByAlcoholListResponse(BaseModel):
    subtypes: List[str]
    feeds: List[FeedByAlcoholResponse] = []

    @classmethod
    def of(cls, feeds: List[FeedByAlcoholResponse], subtypes: List[str]):
        return FeedByAlcoholListResponse(subtypes=subtypes, feeds=feeds)


class FeedLikeResponse(BaseModel):
    feed_id: int
    is_liked: bool

    @classmethod
    def of(cls, feed_id: int, is_liked: bool):
        return FeedLikeResponse(feed_id=feed_id, is_liked=is_liked)


class FeedSearchResponse(BaseModel):
    feed_id: int
    represent_image: str
    title: str
    content: str
    tags: List[str]

    @classmethod
    def of(cls, feed: Feed, tags: List[str]):
        return FeedSearchResponse(
            feed_id=feed.id,
            represent_image=feed.represent_image,
            title=feed.title,
            content=feed.content,
            tags=tags,
        )


class FeedSearchListResponse(BaseModel):
    results: List[FeedSearchResponse]

    @classmethod
    def of(cls, feeds: List[Feed]):
        results = []
        for feed in feeds:
            alcohols = pairing_cache_store.get_all_names_by_ids(
                feed.alcohol_pairing_ids
            )
            foods = pairing_cache_store.get_all_names_by_ids(feed.food_pairing_ids)
            results.append(FeedSearchResponse.of(feed, alcohols + foods))
        return FeedSearchListResponse(results=results)


class FeedAdminResponse(BaseModel):
    feed_id: int
    title: str
    content: str
    is_deleted: bool
    user_id: int
    user_nickname: Optional[str]
    score: float
    represent_image: str
    images: List[str]
    alcohols: List[str]
    foods: List[str]
    user_tags: Optional[List[str]]
    view_count: int
    created_at: datetime
    updated_at: datetime
    is_reported: bool

    @classmethod
    def of(cls, feed: Feed):
        return FeedAdminResponse(
            **feed.__data__,
            feed_id=feed.id,
            user_id=feed.user.id,
            user_nickname=feed.user.nickname,
            alcohols=pairing_cache_store.get_all_names_by_ids(feed.alcohol_pairing_ids),
            foods=pairing_cache_store.get_all_names_by_ids(feed.food_pairing_ids),
        )
