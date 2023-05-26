from typing import List
from typing import Any
from dataclasses import dataclass
import json
@dataclass
class AssetContract:
    address: str
    asset_contract_type: str
    chain_identifier: str
    created_date: str
    name: str
    nft_version: str
    owner: int
    schema_name: str
    symbol: str
    total_supply: int
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
    def from_dict(obj: Any) -> 'AssetContract':
        _address = str(obj.get("address"))
        _asset_contract_type = str(obj.get("asset_contract_type"))
        _chain_identifier = str(obj.get("chain_identifier"))
        _created_date = str(obj.get("created_date"))
        _name = str(obj.get("name"))
        _nft_version = str(obj.get("nft_version"))
        _owner = int(obj.get("owner"))
        _schema_name = str(obj.get("schema_name"))
        _symbol = str(obj.get("symbol"))
        _total_supply = int(obj.get("total_supply"))
        _description = str(obj.get("description"))
        _external_link = str(obj.get("external_link"))
        _image_url = str(obj.get("image_url"))
        _default_to_fiat = str(obj.get("default_to_fiat"))
        _dev_buyer_fee_basis_points = int(obj.get("dev_buyer_fee_basis_points"))
        _dev_seller_fee_basis_points = int(obj.get("dev_seller_fee_basis_points"))
        _only_proxied_transfers = str(obj.get("_only_proxied_transfers"))
        _opensea_buyer_fee_basis_points = int(obj.get("opensea_buyer_fee_basis_points"))
        _opensea_seller_fee_basis_points = int(obj.get("opensea_seller_fee_basis_points"))
        _buyer_fee_basis_points = int(obj.get("buyer_fee_basis_points"))
        _seller_fee_basis_points = int(obj.get("seller_fee_basis_points"))
        _payout_address = str(obj.get("payout_address"))
        return AssetContract(_address, _asset_contract_type, _chain_identifier, _created_date, _name, _nft_version, _owner, _schema_name, _symbol, _total_supply, _description, _external_link, _image_url, _default_to_fiat, _dev_buyer_fee_basis_points, _dev_seller_fee_basis_points, _only_proxied_transfers, _opensea_buyer_fee_basis_points, _opensea_seller_fee_basis_points, _buyer_fee_basis_points, _seller_fee_basis_points, _payout_address)

@dataclass
class Creator:
    address: str
    config: str
    profile_img_url: str

    @staticmethod
    def from_dict(obj: Any) -> 'Creator':
        _address = str(obj.get("address"))
        _config = str(obj.get("config"))
        _profile_img_url = str(obj.get("profile_img_url"))
        return Creator(_address, _config, _profile_img_url)

@dataclass
class DisplayData:
    card_display_style: str

    @staticmethod
    def from_dict(obj: Any) -> 'DisplayData':
        _card_display_style = str(obj.get("card_display_style"))
        return DisplayData(_card_display_style)




@dataclass
class Collection:
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
    is_creator_fees_enforced: bool

    @staticmethod
    def from_dict(obj: Any) -> 'Collection':
        _banner_image_url = str(obj.get("banner_image_url"))
        _chat_url = str(obj.get("chat_url"))
        _created_date = str(obj.get("created_date"))
        _default_to_fiat = bool(obj.get("default_to_fiat"))
        _description = str(obj.get("description"))
        _dev_buyer_fee_basis_points = str(obj.get("dev_buyer_fee_basis_points"))
        _dev_seller_fee_basis_points = str(obj.get("dev_seller_fee_basis_points"))
        _discord_url = str(obj.get("discord_url"))
        _display_data = DisplayData.from_dict(obj.get("display_data"))
        _external_url = str(obj.get("external_url"))
        _featured = bool(obj.get("featured"))
        _featured_image_url = str(obj.get("featured_image_url"))
        _hidden = bool(obj.get("hidden"))
        _safelist_request_status = str(obj.get("safelist_request_status"))
        _image_url = str(obj.get("image_url"))
        _is_subject_to_whitelist = bool(obj.get("is_subject_to_whitelis"))
        _large_image_url = str(obj.get("large_image_url"))
        _medium_username = str(obj.get("medium_username"))
        _name = str(obj.get("name"))
        _only_proxied_transfers = bool(obj.get("only_proxied_transfers"))
        _opensea_buyer_fee_basis_points = str(obj.get("opensea_buyer_fee_basis_points"))
        _opensea_seller_fee_basis_points = int(obj.get("opensea_seller_fee_basis_points"))
        _payout_address = str(obj.get("payout_address"))
        _require_email =  bool(obj.get("require_email"))
        _short_description = str(obj.get("short_description"))
        _slug = str(obj.get("slug"))
        _telegram_url = str(obj.get("telegram_url"))
        _twitter_username = str(obj.get("twitter_username"))
        _instagram_username = str(obj.get("instagram_username"))
        _wiki_url = str(obj.get("wiki_url"))
        _is_nsfw = bool(obj.get("is_nsfw"))
        _is_rarity_enabled = bool(obj.get("is_rarity_enabled"))
        _is_creator_fees_enforced = bool(obj.get("is_creator_fees_enforced"))
        return Collection(_banner_image_url, _chat_url, _created_date, _default_to_fiat, _description, _dev_buyer_fee_basis_points, _dev_seller_fee_basis_points, _discord_url, _display_data, _external_url, _featured, _featured_image_url, _hidden, _safelist_request_status, _image_url, _is_subject_to_whitelist, _large_image_url, _medium_username, _name, _only_proxied_transfers, _opensea_buyer_fee_basis_points, _opensea_seller_fee_basis_points, _payout_address, _require_email, _short_description, _slug, _telegram_url, _twitter_username, _instagram_username, _wiki_url, _is_nsfw, _fees, _is_rarity_enabled, _is_creator_fees_enforced)


@dataclass
class Trait:
    trait_type: str
    display_type: str
    trait_count: int
    value: object

    @staticmethod
    def from_dict(obj: Any) -> 'Trait':
        _trait_type = str(obj.get("trait_type"))
        _display_type = str(obj.get("display_type"))
        _trait_count = int(obj.get("trait_count"))
        _value = obj.get("value")
        return Trait(_trait_type, _display_type, _trait_count, _value)

@dataclass
class OpenSeaAsset:
    id: int
    token_id: str
    num_sales: int
    background_color: str
    image_url: str
    image_preview_url: str
    image_thumbnail_url: str
    image_original_url: str
    name: str
    description: str
    external_link: str
    #asset_contract: AssetContract
    permalink: str
    #collection: Collection
    token_metadata: str
    is_nsfw: bool
    #creator: Creator
    traits: List[Trait]
    supports_wyvern: bool

    @staticmethod
    def from_dict(obj: Any) -> 'OpenSeaAsset':
        _id = int(obj.get("id"))
        _token_id = str(obj.get("token_id"))
        _num_sales = int(obj.get("num_sales"))
        _background_color = str(obj.get("background_color"))
        _image_url = str(obj.get("image_url"))
        _image_preview_url = str(obj.get("image_preview_url"))
        _image_thumbnail_url = str(obj.get("image_thumbnail_url"))
        _image_original_url = str(obj.get("image_original_url"))
        _name = str(obj.get("name"))
        _description = str(obj.get("description"))
        _external_link = str(obj.get("external_link"))
        #_asset_contract = AssetContract.from_dict(obj.get("asset_contract"))
        _permalink = str(obj.get("permalink"))
        #_collection = Collection.from_dict(obj.get("collection"))
        _token_metadata = str(obj.get("token_metadata"))
        _is_nsfw = bool(obj.get("is_nsfw"))
        #_creator = Creator.from_dict(obj.get("creator"))
        _traits = [Trait.from_dict(y) for y in obj.get("traits")]
        _supports_wyvern = bool(obj.get("supports_wyvern"))
        #return OpenSeaAsset(_id, _token_id, _num_sales, _background_color, _image_url, _image_preview_url, _image_thumbnail_url, _image_original_url, _name, _description, _external_link, _asset_contract, _permalink, _collection, _token_metadata, _is_nsfw, _creator, _traits, _supports_wyvern)
        return OpenSeaAsset(_id, _token_id, _num_sales, _background_color, _image_url, _image_preview_url, _image_thumbnail_url, _image_original_url, _name, _description, _external_link, _permalink, _token_metadata, _is_nsfw, _traits, _supports_wyvern)


