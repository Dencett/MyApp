from contextlib import suppress
from typing import Any, Dict, Generator

from django.core.cache import cache
from django.http import HttpRequest

from catalog.common import get_famous_tags, parse_price
from catalog.utils import Params, Sorter, Filter
from products.models import Category


class CatalogContextProcessor:
    pagination_on_each_side: int = 2
    pagination_on_ends: int = 1

    default_sort_name = "famous"
    default_desc = "on"

    def __init__(
        self,
        request: HttpRequest,
        context: Dict[str, Any],
        raw_params: Params,
    ) -> None:
        self.request = request
        self.context = context
        self.__params = raw_params

        self.sorter = Sorter()
        self.filter = Filter(raw_params)

    @property
    def params(self) -> Params:
        return self.__params

    def set_context(self) -> None:
        """
        Context keys:
            params - Params\n
            sort_params - Params\n
            tag_params - Params\n
            category_params - Params\n
            pagination_range - Generator[str, None, None]\n
            famous_tags - List[Tag]\n
            sort - String\n
            desc - String\n
            sort_items - Generator[Tuple[str, str], None, None]\n
            default_price_from - Float\n
            default_price_to - Float\n
        Optional context keys:
            filter_params - Params\n
            current_category - Category\n
            start_price - Float\n
            stop_price - Float\n
            price - String\n
            title - String\n
            remains - Boolean\n
            free_delivery - String\n
            search - String\n
        """
        self.__set_search_context()
        self.__set_category_context()
        self.__set_tags_context()
        self.__set_sort_context()
        self.__set_price_context()
        self.__set_params_context()

    def __set_params_context(self) -> None:
        """
        Context keys:
            params - Params\n
        """
        params = Params()
        params_list = [
            "sort_params",
            "filter_params",
            "tag_params",
            "category_params",
        ]

        for param in params_list:
            params += self.context.get(param, {})

        self.context["params"] = params

    def set_pagination_context(self) -> None:
        """
        Context keys:
            pagination_range - Generator[str, None, None]
        """
        self.context["pagination_range"] = self.__get_pagination_range()

    def __set_tags_context(self) -> None:
        """
        Context keys:
            famous_tags - List[Tag]\n
            tag_params - Params
        """
        tag_id = self.__params.get("tag_id")

        self.context["famous_tags"] = get_famous_tags(6)
        self.context["tag_params"] = Params(tag_id=tag_id) if tag_id else Params()

    def __set_category_context(self) -> None:
        """
        Context keys:
            category_params - Params
        Optional context keys:
            current_category - Category
        """
        category_id = self.__params.get("category_id")

        if category_id:
            self.context["current_category"] = self.__get_current_category(category_id)
            self.context["category_params"] = Params(category_id=category_id)
        else:
            self.context["category_params"] = Params()

    def __set_sort_context(self) -> None:
        """
        Context keys:
            sort_items - Generator[Tuple[str, str], None, None]\n
            sort - String\n
            desc - String\n
            sort_params - Params
        """
        context_data = {
            "sort": self.__params.get("sort") or self.default_sort_name,
            "desc": self.__params.get("desc") or self.default_desc,
            "sort_items": self.sorter.get_items(),
        }

        self.context.update(context_data)

        sort_params = self.__build_sort_params(context_data)

        self.context["sort_params"] = sort_params

    def __set_search_context(self) -> None:
        """
        Optional context keys:
            search - String
        """
        search = self.__params.get("search")

        if search:
            self.context["search"] = search

    def __set_price_context(self) -> None:
        """
        Context keys:
            default_price_from - Float\n
            default_price_to - Float\n
        Optional context keys:
            start_price - Float\n
            stop_price - Float
        """
        prices = parse_price(self.__params.get("price"))

        if prices:
            self.context["start_price"] = prices[0]
            self.context["stop_price"] = prices[1]

        self.context["default_price_from"] = self.filter.default_price_from
        self.context["default_price_to"] = self.filter.default_price_to

    def set_filter_context(self, data: Dict[str, Any] | None = None) -> None:
        """
        Context keys:
            filter_params - Params
        Optional context keys:
            price - String\n
            title - String\n
            remains - Boolean\n
            free_delivery - String
        """
        if not data:
            data = self.__params

        raw_context = {
            "price": data.get("price"),
            "title": data.get("title"),
            "search": data.get("search"),
            "remains": data.get("remains"),
            "free_delivery": data.get("free_delivery"),
        }

        context_data = {}

        for key, value in raw_context.items():
            if value:
                with suppress(KeyError):
                    self.context.pop(key)

                context_data[key] = value

        filter_params = Params(**context_data)

        if filter_params:
            with suppress(KeyError):
                self.context.pop("filter_params")

            context_data["filter_params"] = filter_params
        else:
            context_data["filter_params"] = Params()

        self.context.update(context_data)

    def __get_pagination_range(self) -> Generator[str, None, None]:
        page_number = self.request.GET.get("page")

        if not page_number:
            page_number = 1

        return self.context["paginator"].get_elided_page_range(
            number=page_number,
            on_each_side=self.pagination_on_each_side,
            on_ends=self.pagination_on_ends,
        )

    def __get_current_category(self, category_id: str) -> Category:
        cache_key = "categories_data_export"
        categories_list = cache.get(cache_key)

        for category in categories_list:
            if str(category.pk) == category_id:
                return category

    def __build_sort_params(self, data: Dict[str, Any]) -> Params:
        return Params(sort=data["sort"], desc="on" if data["desc"] == "on" else "off")
