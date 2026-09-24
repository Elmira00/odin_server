#odin2/project/management/auto_healer/resolvers_adapter.py
"""
Thin adapters: wrap each existing per-field healer from resolvers.py so it
emits Candidate objects instead of a final {"resolution_type", "rule"}
dict directly. The healer's internal find_*()/check_meta_tags()/
get_json_ld_value() logic is untouched -- only the outermost method
changes, per field.
"""
from management.auto_healer.candidates import Candidate
from management.auto_healer.resolvers import (
    ContentAutoHealer as _ContentAutoHealer,
    TitleAutoHealer as _TitleAutoHealer,
    DescriptionAutoHealer as _DescriptionAutoHealer,
    ImageAutoHealer as _ImageAutoHealer,
    SharedDateAutoHealer as _SharedDateAutoHealer,
)


class ContentAutoHealer(_ContentAutoHealer):
    def get_base_candidates(self, soup, field, url):
        if field != "content":
            return []
        node = self.find_content(soup)
        if not node:
            return []
        return [Candidate(
            field="content",
            resolution_type="css_selector",
            rule=self.generate_css_selector(node),
            source="base",
            node=node,
            prior_confidence=0.5,
        )]


class TitleAutoHealer(_TitleAutoHealer):
    def get_base_candidates(self, soup, field, url):
        if field != "title":
            return []

        candidates = []

        # DOM guess.
        node = self.find_title(soup)
        if node:
            candidates.append(Candidate(
                field="title",
                resolution_type="css_selector",
                rule=self.generate_css_selector(node),
                source="base",
                node=node,
                prior_confidence=0.5,
            ))

        # JSON-LD headline, contributed as its own candidate rather than an
        # early-return, so the shared scorer in discovery.py decides which
        # one wins (see the run_diagnostics comment in resolvers.py for why
        # JSON-LD isn't blindly trusted over the real rendered DOM text).
        json_ld_headline = self.get_json_ld_value(soup, self.json_ld_keys)
        if json_ld_headline:
            candidates.append(Candidate(
                field="title",
                resolution_type="json_ld",
                rule={"source": "json_ld", "keys": self.json_ld_keys},
                source="base_json_ld",
                value=json_ld_headline,
                prior_confidence=0.7,
            ))

        # Standard meta tags.
        meta_value, meta_rule = self.check_meta_tags(soup, self.meta_tags)
        if meta_value:
            candidates.append(Candidate(
                field="title",
                resolution_type="meta",
                rule=meta_rule,
                source="base_meta",
                value=meta_value,
                prior_confidence=0.6,
            ))

        return candidates


class DescriptionAutoHealer(_DescriptionAutoHealer):
    def get_base_candidates(self, soup, field, url):
        if field != "description":
            return []

        candidates = []

        json_ld_desc = self.get_json_ld_value(soup, self.json_ld_keys)
        if json_ld_desc and len(json_ld_desc.strip()) > 15:
            candidates.append(Candidate(
                field="description",
                resolution_type="json_ld",
                rule={"source": "json_ld", "keys": self.json_ld_keys},
                source="base_json_ld",
                value=json_ld_desc,
                prior_confidence=0.75,
            ))

        meta_value, meta_rule = self.check_meta_tags(soup, self.meta_tags)
        if meta_value and len(meta_value.strip()) > 5:
            candidates.append(Candidate(
                field="description",
                resolution_type="meta",
                rule=meta_rule,
                source="base_meta",
                value=meta_value,
                prior_confidence=0.65,
            ))

        node = self.find_description(soup)
        if node:
            candidates.append(Candidate(
                field="description",
                resolution_type="css_selector",
                rule=self.generate_css_selector(node),
                source="base",
                node=node,
                prior_confidence=0.4,
            ))

        return candidates


class ImageAutoHealer(_ImageAutoHealer):
    def get_base_candidates(self, soup, field, url):
        if field != "image":
            return []

        candidates = []

        meta_value, meta_rule = self.check_meta_tags(soup, self.meta_tags)
        if meta_value:
            candidates.append(Candidate(
                field="image",
                resolution_type="meta",
                rule=meta_rule,
                source="base_meta",
                value=meta_value,
                prior_confidence=0.7,
            ))

        target_node_tfidf = self.find_image_by_tf_idf(soup)
        target_node_heur = self.find_image_by_heuristic_score(soup)
        target_node_h1 = self.find_image_by_h1_proximity(soup)

        for node, conf in ((target_node_heur, 0.5), (target_node_tfidf, 0.4), (target_node_h1, 0.4)):
            if node:
                candidates.append(Candidate(
                    field="image",
                    resolution_type="css_selector",
                    rule=self.generate_css_selector(node),
                    source="base",
                    node=node,
                    prior_confidence=conf,
                ))

        return candidates


class SharedDateAutoHealer(_SharedDateAutoHealer):
    def get_base_candidates(self, soup, field, url):
        if field != "shared_date":
            return []

        candidates = []

        json_ld_date = self.get_json_ld_value(soup, self.json_ld_keys)
        if json_ld_date:
            candidates.append(Candidate(
                field="shared_date",
                resolution_type="json_ld",
                rule={"source": "json_ld", "keys": self.json_ld_keys},
                source="base_json_ld",
                value=json_ld_date,
                prior_confidence=0.8,
            ))

        meta_value, meta_rule = self.check_meta_tags(soup, self.meta_tags)
        if meta_value:
            candidates.append(Candidate(
                field="shared_date",
                resolution_type="meta",
                rule=meta_rule,
                source="base_meta",
                value=meta_value,
                prior_confidence=0.7,
            ))

        node = self.find_date_node(soup)
        if node:
            candidates.append(Candidate(
                field="shared_date",
                resolution_type="css_selector",
                rule=self.generate_css_selector(node),
                source="base",
                node=node,
                prior_confidence=0.4,
            ))

        return candidates