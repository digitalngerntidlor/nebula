"""Query builders for the GA4 active-user DuckDB cache."""

ACTIVE_USERS_QUERY = r"""
SELECT DISTINCT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  'heygoody' AS site,
  'article' AS segment,
  user_pseudo_id
FROM `heygoody-450609.analytics_327162452.events_*`
WHERE _TABLE_SUFFIX BETWEEN @suffix_start AND @suffix_end
  AND stream_id = '3983610913'
  AND device.web_info.hostname = 'www.heygoody.com'
  AND REGEXP_CONTAINS(session_traffic_source_last_click.cross_channel_campaign.primary_channel_group, r'(?i)^(Organic Search|Direct)$')
  AND is_active_user = TRUE
  AND EXISTS (
    SELECT 1 FROM UNNEST(event_params) AS ep
    WHERE ep.key = 'page_location'
      AND REGEXP_CONTAINS(ep.value.string_value, r'blogs')
  )

UNION ALL

SELECT DISTINCT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  'heygoody' AS site,
  'product' AS segment,
  user_pseudo_id
FROM `heygoody-450609.analytics_327162452.events_*`
WHERE _TABLE_SUFFIX BETWEEN @suffix_start AND @suffix_end
  AND stream_id = '3983610913'
  AND device.web_info.hostname = 'www.heygoody.com'
  AND REGEXP_CONTAINS(session_traffic_source_last_click.cross_channel_campaign.primary_channel_group, r'(?i)^(Organic Search|Direct)$')
  AND is_active_user = TRUE
  AND EXISTS (
    SELECT 1 FROM UNNEST(event_params) AS ep
    WHERE ep.key = 'page_location'
      AND REGEXP_CONTAINS(
            REGEXP_EXTRACT(ep.value.string_value, r'https?://[^/]+(/[^?#]*)'),
            r'^(/th)?/(autoinsurance.*|travelinsurance.*|homeinsurance.*|cancer.*|critical-illness.*|tax-deduction.*|travel-insurance.*|checkinsurance.*|auto-short-term.*|checkout.*|affiliates.*|chat-commerce.*|cs-sale.*)(/.*)?$'
          )
  )

UNION ALL

SELECT DISTINCT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  'tidlor' AS site,
  'article' AS segment,
  user_pseudo_id
FROM `ngerntidlor-440109.analytics_232252865.events_*`
WHERE _TABLE_SUFFIX BETWEEN @suffix_start AND @suffix_end
  AND stream_id = '2042874482'
  AND device.web_info.hostname = 'www.tidlor.com'
  AND REGEXP_CONTAINS(session_traffic_source_last_click.cross_channel_campaign.primary_channel_group, r'(?i)^(Organic Search|Direct)$')
  AND is_active_user = TRUE
  AND EXISTS (
    SELECT 1 FROM UNNEST(event_params) AS ep
    WHERE ep.key = 'page_location'
      AND REGEXP_CONTAINS(ep.value.string_value, r'article')
  )

UNION ALL

SELECT DISTINCT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  'tidlor' AS site,
  'product' AS segment,
  user_pseudo_id
FROM `ngerntidlor-440109.analytics_232252865.events_*`
WHERE _TABLE_SUFFIX BETWEEN @suffix_start AND @suffix_end
  AND stream_id = '2042874482'
  AND device.web_info.hostname = 'www.tidlor.com'
  AND REGEXP_CONTAINS(session_traffic_source_last_click.cross_channel_campaign.primary_channel_group, r'(?i)^(Organic Search|Direct)$')
  AND is_active_user = TRUE
  AND EXISTS (
    SELECT 1 FROM UNNEST(event_params) AS ep
    WHERE ep.key = 'page_location'
      AND REGEXP_CONTAINS(
            REGEXP_EXTRACT(ep.value.string_value, r'https?://[^/]+(/[^?#]*)'),
            r'^/th/(loan.*|autoloan.*|loancal.*|loaninfo.*|thank-you.*|.*true-money.*|pdpa.*)(/.*)?$'
          )
      AND NOT REGEXP_CONTAINS(ep.value.string_value, r'mode|platform')
  )

UNION ALL

SELECT DISTINCT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  'tidloh' AS site,
  'article' AS segment,
  user_pseudo_id
FROM `ngerntidlor-440109.analytics_415907532.events_*`
WHERE _TABLE_SUFFIX BETWEEN @suffix_start AND @suffix_end
  AND stream_id = '6374486653'
  AND REGEXP_CONTAINS(device.web_info.hostname, r'^(prakantidloh\.tidlor\.com|www\.prakantidloh\.com)$')
  AND REGEXP_CONTAINS(session_traffic_source_last_click.cross_channel_campaign.primary_channel_group, r'(?i)^(Organic Search|Direct)$')
  AND is_active_user = TRUE
  AND EXISTS (
    SELECT 1 FROM UNNEST(event_params) AS ep
    WHERE ep.key = 'page_location'
      AND REGEXP_CONTAINS(ep.value.string_value, r'article')
      AND NOT REGEXP_CONTAINS(ep.value.string_value, r'mode|platform')
  )

UNION ALL

SELECT DISTINCT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  'tidloh' AS site,
  'product' AS segment,
  user_pseudo_id
FROM `ngerntidlor-440109.analytics_415907532.events_*`
WHERE _TABLE_SUFFIX BETWEEN @suffix_start AND @suffix_end
  AND stream_id = '6374486653'
  AND REGEXP_CONTAINS(device.web_info.hostname, r'^(prakantidloh\.tidlor\.com|www\.prakantidloh\.com)$')
  AND REGEXP_CONTAINS(session_traffic_source_last_click.cross_channel_campaign.primary_channel_group, r'(?i)^(Organic Search|Direct)$')
  AND is_active_user = TRUE
  AND EXISTS (
    SELECT 1 FROM UNNEST(event_params) AS ep
    WHERE ep.key = 'page_location'
      AND REGEXP_CONTAINS(
            REGEXP_EXTRACT(ep.value.string_value, r'https?://[^/]+(/[^?#]*)'),
            r'^/(insurance.*|thankyou.*).*$'
          )
      AND NOT REGEXP_CONTAINS(ep.value.string_value, r'mode|platform')
  )
"""

MERGE_QUERY = """
MERGE `heygoody-450609.SEO.Traffic_and_Conversion_All_ga4_cache` T
USING UNNEST(@rows) AS S
ON T.year_str = S.year_str AND T.month_str = S.month_str
WHEN MATCHED THEN UPDATE SET
  active_users_article_heygoody = S.active_users_article_heygoody,
  active_users_product_heygoody = S.active_users_product_heygoody,
  active_users_article_tidlor   = S.active_users_article_tidlor,
  active_users_product_tidlor   = S.active_users_product_tidlor,
  active_users_article_tidloh   = S.active_users_article_tidloh,
  active_users_product_tidloh   = S.active_users_product_tidloh,
  last_refreshed_at             = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (
  year_str,
  month_str,
  active_users_article_heygoody,
  active_users_product_heygoody,
  active_users_article_tidlor,
  active_users_product_tidlor,
  active_users_article_tidloh,
  active_users_product_tidloh,
  last_refreshed_at
) VALUES (
  S.year_str,
  S.month_str,
  S.active_users_article_heygoody,
  S.active_users_product_heygoody,
  S.active_users_article_tidlor,
  S.active_users_product_tidlor,
  S.active_users_article_tidloh,
  S.active_users_product_tidloh,
  CURRENT_TIMESTAMP()
)
"""


def build_active_users_query() -> str:
    return ACTIVE_USERS_QUERY


def build_merge_query() -> str:
    return MERGE_QUERY
