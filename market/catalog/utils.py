from typing import Tuple, Any, Dict, Generator, List

from django.db.models import QuerySet, Count, F, Q

from catalog.common import Params
from catalog.forms import CatalogFilterForm


class Filter:
    default_price_from: float = 10.00
    default_price_to: float = 1000.00

    def __init__(self, params: Params) -> None:
        self.__params = params

    def extract_by_form_fields(self, data: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not data:
            data = {}

        for field in CatalogFilterForm().fields:
            param_value = self.__params.get(field)

            if param_value:
                data[field] = param_value

        return data

    def extract_additional_params_data(self, data: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not data:
            data = {}

        category_id = self.__params.get("category_id")
        if category_id:
            data["category_id"] = category_id

        return data

    def __extract_params_data(self) -> Dict[str, Any]:
        data = self.extract_by_form_fields()
        data = self.extract_additional_params_data(data)

        return data

    def build_params(self) -> Params:
        return Params(**self.__extract_params_data())

    @classmethod
    def parse_price(cls, price: str | None = None) -> Tuple[float, float] | None:
        if not price:
            return

        prices = price.split(";")

        if len(prices) != 2:
            return

        try:
            return float(prices[0]), float(prices[1])

        except ValueError:
            return

    def __add_price_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prices = self.parse_price(data.get("price"))

        if prices:
            data["start_price"] = prices[0]
            data["stop_price"] = prices[1]

        return data

    def get_context_data(self) -> Dict[str, Any]:
        data = self.__extract_params_data()
        data = self.__add_price_context(data)

        data["default_price_from"] = self.default_price_from
        data["default_price_to"] = self.default_price_to

        return data

    def __price_filter(self, field: str | None = None) -> Dict[str, Tuple[float, float]]:
        """
        Offer price filer
        """
        if not field:
            field = "price"

        data_from_context = self.get_context_data()

        start_price = data_from_context.get("start_price", self.default_price_from)
        stop_price = data_from_context.get("stop_price", self.default_price_to)

        return {f"{field}__range": (start_price, stop_price)}

    def __delivery_filter(self, field: str | None = None) -> Dict[str, str]:
        """
        Offer delivery filer
        """
        if not field:
            field = "delivery_method"

        return {field: "REGULAR"}

    def __product_search_filter(self, value: str, fields: List[str] | Tuple[str, str] | None = None) -> Q:
        """
        Product search filer
        """
        if not fields:
            fields = "about", "name"

        return Q(**{f"product__{fields[0]}__contains": value}) | Q(**{f"product__{fields[0]}__contains": value})

    def __category_available_filter(self) -> Dict[str, bool]:
        """
        Category available filter
        """
        return {
            "product__category__is_active": True,
            "product__category__archived": False,
        }

    def __category_filter(self, value: str) -> Dict[str, Any]:
        """
        Product category filter
        """
        return {"product__category__pk": value}

    def __remain_filter(self, field: str | None = None) -> Dict[str, int]:
        """
        Offer remain filter
        """
        if not field:
            field = "remains"

        return {f"{field}__gte": 1}

    def filter_offer(self, queryset: QuerySet) -> QuerySet:
        filter_: Dict[str, Any] = {}

        if "price" in self.__params.items:
            filter_.update(self.__price_filter("price"))

        if "free_delivery" in self.__params.items:
            filter_.update(self.__delivery_filter("delivery_method"))

        if "remains" in self.__params.items:
            filter_.update(self.__remain_filter("remains"))

        return queryset.filter(**filter_)

    def filter_prodict(self, queryset: QuerySet) -> QuerySet:
        filter_kwargs: Dict[str, Any] = {}
        filter_args = []

        search_or_title_value = self.__params.items.get("title", self.__params.items.get("search"))

        if search_or_title_value:
            filter_args.append(self.__product_search_filter(search_or_title_value))

        category_id = self.__params.get("category_id")

        if category_id:
            filter_kwargs.update(self.__category_filter(category_id))

        filter_kwargs.update(self.__category_available_filter())

        return queryset.filter(*filter_args, **filter_kwargs)


class Sorter:
    default_sort = "pk"
    default_sort_name = "famous"
    default_sort_desc = "on"

    sort_types = {
        "famous": "Популярности",
        "price": "Цене",
        "review": "Отзывам",
        "recency": "Новизне",
    }

    def __init__(self, params: Params) -> None:
        self.__params = params

    def build_params(self) -> Params:
        sort = self.__params.get("sort") or self.default_sort_name
        sort_desc = "on" if self.__params.get("sort_desc") == "on" else "off"

        return Params(sort=sort, sort_desc=sort_desc)

    def __get_items(self) -> Generator:
        for name, title in self.sort_types.items():
            yield name, title

    def get_context_data(self) -> Dict[str, str]:
        sort = self.__params.get("sort") or self.default_sort_name
        sort_desc = self.__params.get("sort_desc") or self.default_sort_desc

        return {
            "sort": sort,
            "sort_desc": sort_desc,
            "sort_items": self.__get_items(),
        }

    def sort(self, queryset: QuerySet) -> QuerySet:
        params = self.build_params()

        sort = params.get("sort")
        desc = params.get("sort_desc")

        if not sort:
            return queryset.order_by(self.default_sort)

        if sort == "famous":
            return self._sort_by_famous(queryset, desc)

        if sort == "price":
            return self._sort_by_price(queryset, desc)

        if sort == "review":
            return self._sort_by_review(queryset, desc)

        if sort == "recency":
            return self._sort_by_recency(queryset, desc)

    def _sort_by_famous(self, queryset: QuerySet, desc: str) -> QuerySet:
        return queryset.order_by(self.default_sort)  # TODO: добавить сортировку по популярности

    def _sort_by_price(self, queryset: QuerySet, desc: str) -> QuerySet:
        if desc == "on":
            param = F("price").desc()
        else:
            param = F("price").asc()

        return queryset.order_by(param)

    def _sort_by_review(self, queryset: QuerySet, desc: str) -> QuerySet:
        if desc == "on":
            param = F("review_count").desc()
        else:
            param = F("review_count").asc()

        return queryset.annotate(review_count=Count(F("product__review"))).order_by(param)

    def _sort_by_recency(self, queryset: QuerySet, desc: str) -> QuerySet:
        if desc == "on":
            param = F("product__manufacturer__modified_at").desc()
        else:
            param = F("product__manufacturer__modified_at").asc()

        return queryset.order_by(param)
