from typing import List
from typing import Any
from dataclasses import dataclass
import json

@dataclass
class DisplayData:
    card_display_style: str

    @staticmethod
    def from_dict(obj: Any) -> 'DisplayData':
        _card_display_style = str(obj.get("card_display_style"))
        return DisplayData(_card_display_style)

@dataclass
class DistanceToDistrict:
    min: int
    max: int

    @staticmethod
    def from_dict(obj: Any) -> 'DistanceToDistrict':
        _min = int(obj.get("min"))
        _max = int(obj.get("max"))
        return DistanceToDistrict(_min, _max)

@dataclass
class DistanceToPlaza:
    min: int
    max: int

    @staticmethod
    def from_dict(obj: Any) -> 'DistanceToPlaza':
        _min = int(obj.get("min"))
        _max = int(obj.get("max"))
        return DistanceToPlaza(_min, _max)

@dataclass
class DistanceToRoad:
    min: int
    max: int

    @staticmethod
    def from_dict(obj: Any) -> 'DistanceToRoad':
        _min = int(obj.get("min"))
        _max = int(obj.get("max"))
        return DistanceToRoad(_min, _max)






@dataclass
class PrimaryAssetContract:
    address: str
    asset_contract_type: str
    chain_identifier: str
    created_date: str
    name: str
    nft_version: str
    opensea_version: str
    owner: object
    schema_name: str
    symbol: str
    total_supply: str
    description: str
    external_link: str
    image_url: str
    default_to_fiat: bool
    dev_buyer_fee_basis_points: int
    dev_seller_fee_basis_points: int
    only_proxied_transfers: bool
    opensea_buyer_fee_basis_points: int
    opensea_seller_fee_basis_points: int
    buyer_fee_basis_points: int
    seller_fee_basis_points: int
    payout_address: str

    @staticmethod
    def from_dict(obj: Any) -> 'PrimaryAssetContract':
        _address = str(obj.get("address"))
        _asset_contract_type = str(obj.get("asset_contract_type"))
        _chain_identifier = str(obj.get("chain_identifier"))
        _created_date = str(obj.get("created_date"))
        _name = str(obj.get("name"))
        _nft_version = str(obj.get("nft_version"))
        _opensea_version = str(obj.get("opensea_version"))
        _owner = str(obj.get("owner"))
        _schema_name = str(obj.get("schema_name"))
        _symbol = str(obj.get("symbol"))
        _total_supply = str(obj.get("total_supply"))
        _description = str(obj.get("description"))
        _external_link = str(obj.get("external_link"))
        _image_url = str(obj.get("image_url"))
        _default_to_fiat = bool
        _dev_buyer_fee_basis_points = int(obj.get("dev_buyer_fee_basis_points"))
        _dev_seller_fee_basis_points = int(obj.get("dev_seller_fee_basis_points"))
        _only_proxied_transfers = bool
        _opensea_buyer_fee_basis_points = int(obj.get("opensea_buyer_fee_basis_points"))
        _opensea_seller_fee_basis_points = int(obj.get("opensea_seller_fee_basis_points"))
        _buyer_fee_basis_points = int(obj.get("buyer_fee_basis_points"))
        _seller_fee_basis_points = int(obj.get("seller_fee_basis_points"))
        _payout_address = str(obj.get("payout_address"))
        return PrimaryAssetContract(_address, _asset_contract_type, _chain_identifier, _created_date, _name, _nft_version, _opensea_version, _owner, _schema_name, _symbol, _total_supply, _description, _external_link, _image_url, _default_to_fiat, _dev_buyer_fee_basis_points, _dev_seller_fee_basis_points, _only_proxied_transfers, _opensea_buyer_fee_basis_points, _opensea_seller_fee_basis_points, _buyer_fee_basis_points, _seller_fee_basis_points, _payout_address)



@dataclass
class Size:
    min: int
    max: int

    @staticmethod
    def from_dict(obj: Any) -> 'Size':
        _min = int(obj.get("min"))
        _max = int(obj.get("max"))
        return Size(_min, _max)

@dataclass
class Stats:
    one_minute_volume: float
    one_minute_change: float
    one_minute_sales: float
    one_minute_sales_change: float
    one_minute_average_price: float
    one_minute_difference: float
    five_minute_volume: float
    five_minute_change: float
    five_minute_sales: float
    five_minute_sales_change: float
    five_minute_average_price: float
    five_minute_difference: float
    fifteen_minute_volume: float
    fifteen_minute_change: float
    fifteen_minute_sales: float
    fifteen_minute_sales_change: float
    fifteen_minute_average_price: float
    fifteen_minute_difference: float
    thirty_minute_volume: float
    thirty_minute_change: float
    thirty_minute_sales: float
    thirty_minute_sales_change: float
    thirty_minute_average_price: float
    thirty_minute_difference: float
    one_hour_volume: float
    one_hour_change: float
    one_hour_sales: float
    one_hour_sales_change: float
    one_hour_average_price: float
    one_hour_difference: float
    six_hour_volume: float
    six_hour_change: float
    six_hour_sales: float
    six_hour_sales_change: float
    six_hour_average_price: float
    six_hour_difference: float
    one_day_volume: float
    one_day_change: float
    one_day_sales: float
    one_day_sales_change: float
    one_day_average_price: float
    one_day_difference: float
    seven_day_volume: float
    seven_day_change: float
    seven_day_sales: float
    seven_day_average_price: float
    seven_day_difference: float
    thirty_day_volume: float
    thirty_day_change: float
    thirty_day_sales: float
    thirty_day_average_price: float
    thirty_day_difference: float
    total_volume: float
    total_sales: float
    total_supply: float
    count: float
    num_owners: int
    average_price: float
    num_reports: int
    market_cap: float
    floor_price: float

    @staticmethod
    def from_dict(obj: Any) -> 'Stats':
        _one_minute_volume = float(obj.get("one_minute_volume"))
        _one_minute_change = float(obj.get("one_minute_change"))
        _one_minute_sales = float(obj.get("one_minute_sales"))
        _one_minute_sales_change = float(obj.get("one_minute_sales_change"))
        _one_minute_average_price = float(obj.get("one_minute_average_price"))
        _one_minute_difference = float(obj.get("one_minute_difference"))
        _five_minute_volume = float(obj.get("five_minute_volume"))
        _five_minute_change = float(obj.get("five_minute_change"))
        _five_minute_sales = float(obj.get("five_minute_sales"))
        _five_minute_sales_change = float(obj.get("five_minute_sales_change"))
        _five_minute_average_price = float(obj.get("five_minute_average_price"))
        _five_minute_difference = float(obj.get("five_minute_difference"))
        _fifteen_minute_volume = float(obj.get("fifteen_minute_volume"))
        _fifteen_minute_change = float(obj.get("fifteen_minute_change"))
        _fifteen_minute_sales = float(obj.get("fifteen_minute_sales"))
        _fifteen_minute_sales_change = float(obj.get("fifteen_minute_sales_change"))
        _fifteen_minute_average_price = float(obj.get("fifteen_minute_average_price"))
        _fifteen_minute_difference = float(obj.get("fifteen_minute_difference"))
        _thirty_minute_volume = float(obj.get("thirty_minute_volume"))
        _thirty_minute_change = float(obj.get("thirty_minute_change"))
        _thirty_minute_sales = float(obj.get("thirty_minute_sales"))
        _thirty_minute_sales_change = float(obj.get("thirty_minute_sales_change"))
        _thirty_minute_average_price = float(obj.get("thirty_minute_average_price"))
        _thirty_minute_difference = float(obj.get("thirty_minute_difference"))
        _one_hour_volume = float(obj.get("one_hour_volume"))
        _one_hour_change = float(obj.get("one_hour_change"))
        _one_hour_sales = float(obj.get("one_hour_sales"))
        _one_hour_sales_change = float(obj.get("one_hour_sales_change"))
        _one_hour_average_price = float(obj.get("one_hour_average_price"))
        _one_hour_difference = float(obj.get("one_hour_difference"))
        _six_hour_volume = float(obj.get("six_hour_volume"))
        _six_hour_change = float(obj.get("six_hour_change"))
        _six_hour_sales = float(obj.get("six_hour_sales"))
        _six_hour_sales_change = float(obj.get("six_hour_sales_change"))
        _six_hour_average_price = float(obj.get("six_hour_average_price"))
        _six_hour_difference = float(obj.get("six_hour_difference"))
        _one_day_volume = float(obj.get("one_day_volume"))
        _one_day_change = float(obj.get("one_day_change"))
        _one_day_sales = float(obj.get("one_day_sales"))
        _one_day_sales_change = float(obj.get("one_day_sales_change"))
        _one_day_average_price = float(obj.get("one_day_average_price"))
        _one_day_difference = float(obj.get("one_day_difference"))
        _seven_day_volume = float(obj.get("seven_day_volume"))
        _seven_day_change = float(obj.get("seven_day_change"))
        _seven_day_sales = float(obj.get("seven_day_sales"))
        _seven_day_average_price = float(obj.get("seven_day_average_price"))
        _seven_day_difference = float(obj.get("seven_day_difference"))
        _thirty_day_volume = float(obj.get("thirty_day_volume"))
        _thirty_day_change = float(obj.get("thirty_day_change"))
        _thirty_day_sales = float(obj.get("thirty_day_sales"))
        _thirty_day_average_price = float(obj.get("thirty_day_average_price"))
        _thirty_day_difference = float(obj.get("thirty_day_difference"))
        _total_volume = float(obj.get("total_volume"))
        _total_sales = float(obj.get("total_sales"))
        _total_supply = float(obj.get("total_supply"))
        _count = float(obj.get("count"))
        _num_owners = int(obj.get("num_owners"))
        _average_price = float(obj.get("average_price"))
        _num_reports = int(obj.get("num_reports"))
        _market_cap = float(obj.get("market_cap"))
        _floor_price = float(obj.get("floor_price"))
        return Stats(_one_minute_volume, _one_minute_change, _one_minute_sales, _one_minute_sales_change, _one_minute_average_price, _one_minute_difference, _five_minute_volume, _five_minute_change, _five_minute_sales, _five_minute_sales_change, _five_minute_average_price, _five_minute_difference, _fifteen_minute_volume, _fifteen_minute_change, _fifteen_minute_sales, _fifteen_minute_sales_change, _fifteen_minute_average_price, _fifteen_minute_difference, _thirty_minute_volume, _thirty_minute_change, _thirty_minute_sales, _thirty_minute_sales_change, _thirty_minute_average_price, _thirty_minute_difference, _one_hour_volume, _one_hour_change, _one_hour_sales, _one_hour_sales_change, _one_hour_average_price, _one_hour_difference, _six_hour_volume, _six_hour_change, _six_hour_sales, _six_hour_sales_change, _six_hour_average_price, _six_hour_difference, _one_day_volume, _one_day_change, _one_day_sales, _one_day_sales_change, _one_day_average_price, _one_day_difference, _seven_day_volume, _seven_day_change, _seven_day_sales, _seven_day_average_price, _seven_day_difference, _thirty_day_volume, _thirty_day_change, _thirty_day_sales, _thirty_day_average_price, _thirty_day_difference, _total_volume, _total_sales, _total_supply, _count, _num_owners, _average_price, _num_reports, _market_cap, _floor_price)

@dataclass
class Type:
    land: int
    estate: int

    @staticmethod
    def from_dict(obj: Any) -> 'Type':
        _land = int(obj.get("land"))
        _estate = int(obj.get("estate"))
        return Type(_land, _estate)

@dataclass
class X:
    min: int
    max: int

    @staticmethod
    def from_dict(obj: Any) -> 'X':
        _min = int(obj.get("min"))
        _max = int(obj.get("max"))
        return X(_min, _max)

@dataclass
class Y:
    min: int
    max: int

    @staticmethod
    def from_dict(obj: Any) -> 'Y':
        _min = int(obj.get("min"))
        _max = int(obj.get("max"))
        return Y(_min, _max)


@dataclass
class Traits:
    DistanceToDistrict: DistanceToDistrict
    DistanceToPlaza: DistanceToPlaza
    DistanceToRoad: DistanceToRoad
    Size: Size
    X: X
    Y: Y
    Type: Type

    @staticmethod
    def from_dict(obj: Any) -> 'Traits':
        _DistanceToDistrict = DistanceToDistrict.from_dict(obj.get("Distance to District"))
        _DistanceToPlaza = DistanceToPlaza.from_dict(obj.get("Distance to Plaza"))
        _DistanceToRoad = DistanceToRoad.from_dict(obj.get("Distance to Road"))
        _Size = Size.from_dict(obj.get("Size"))
        _X = X.from_dict(obj.get("X"))
        _Y = Y.from_dict(obj.get("Y"))
        _Type = Type.from_dict(obj.get("Type"))
        return Traits(_DistanceToDistrict, _DistanceToPlaza, _DistanceToRoad, _Size, _X, _Y, _Type)


@dataclass
class OpenSeaCollection:
    is_collection_offers_enabled: bool
    is_trait_offers_enabled: bool
    primary_asset_contracts: List[PrimaryAssetContract]
    traits: Traits
    stats: Stats
    banner_image_url: str
    chat_url: str
    created_date: str
    default_to_fiat: bool
    description: str
    dev_buyer_fee_basis_points: str
    dev_seller_fee_basis_points: str
    discord_url: str
    display_data: DisplayData
    external_url: str
    featured: bool
    featured_image_url: str
    hidden: bool
    safelist_request_status: str
    image_url: str
    is_subject_to_whitelist: bool
    large_image_url: str
    medium_username: str
    name: str
    only_proxied_transfers: bool
    opensea_buyer_fee_basis_points: str
    opensea_seller_fee_basis_points: int
    payout_address: str
    require_email: bool
    short_description: str
    slug: str
    telegram_url: str
    twitter_username: str
    instagram_username: str
    wiki_url: str
    is_nsfw: bool
    is_rarity_enabled: bool

    @staticmethod
    def from_dict(obj: Any) -> 'OpenSeaCollection':
        _is_collection_offers_enabled = bool
        _is_trait_offers_enabled = bool
        _primary_asset_contracts = [PrimaryAssetContract.from_dict(y) for y in obj.get("primary_asset_contracts")]
        _traits = Traits.from_dict(obj.get("traits"))
        _stats = Stats.from_dict(obj.get("stats"))
        _banner_image_url = str(obj.get("banner_image_url"))
        _chat_url = str(obj.get("chat_url"))
        _created_date = str(obj.get("created_date"))
        _default_to_fiat = bool
        _description = str(obj.get("description"))
        _dev_buyer_fee_basis_points = str(obj.get("dev_buyer_fee_basis_points"))
        _dev_seller_fee_basis_points = str(obj.get("dev_seller_fee_basis_points"))
        _discord_url = str(obj.get("discord_url"))
        _display_data = DisplayData.from_dict(obj.get("display_data"))
        _external_url = str(obj.get("external_url"))
        _featured = bool
        _featured_image_url = str(obj.get("featured_image_url"))
        _hidden = bool
        _safelist_request_status = str(obj.get("safelist_request_status"))
        _image_url = str(obj.get("image_url"))
        _is_subject_to_whitelist = bool
        _large_image_url = str(obj.get("large_image_url"))
        _medium_username = str(obj.get("medium_username"))
        _name = str(obj.get("name"))
        _only_proxied_transfers = bool
        _opensea_buyer_fee_basis_points = str(obj.get("opensea_buyer_fee_basis_points"))
        _opensea_seller_fee_basis_points = int(obj.get("opensea_seller_fee_basis_points"))
        _payout_address = str(obj.get("payout_address"))
        _require_email = bool
        _short_description = str(obj.get("short_description"))
        _slug = str(obj.get("slug"))
        _telegram_url = str(obj.get("telegram_url"))
        _twitter_username = str(obj.get("twitter_username"))
        _instagram_username = str(obj.get("instagram_username"))
        _wiki_url = str(obj.get("wiki_url"))
        _is_nsfw = bool
        _is_rarity_enabled = bool
        return OpenSeaCollection(_is_collection_offers_enabled, _is_trait_offers_enabled, _primary_asset_contracts, _traits, _stats, _banner_image_url, _chat_url, _created_date, _default_to_fiat, _description, _dev_buyer_fee_basis_points, _dev_seller_fee_basis_points, _discord_url, _display_data, _external_url, _featured, _featured_image_url, _hidden, _safelist_request_status, _image_url, _is_subject_to_whitelist, _large_image_url, _medium_username, _name, _only_proxied_transfers, _opensea_buyer_fee_basis_points, _opensea_seller_fee_basis_points, _payout_address, _require_email, _short_description, _slug, _telegram_url, _twitter_username, _instagram_username, _wiki_url, _is_nsfw, _is_rarity_enabled)



@dataclass
class Root:
    collection: OpenSeaCollection

    @staticmethod
    def from_dict(obj: Any) -> 'Root':
        _collection = OpenSeaCollection.from_dict(obj.get("collection"))
        return Root(_collection)
