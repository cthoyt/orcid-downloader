"""Utilities for ROR."""

from __future__ import annotations

from functools import lru_cache
from typing import cast

import curies
import gilda
import pyobo
import ssslm

__all__ = [
    "RORGrounder",
    "get_ror_grounder",
]


class RORGrounder(gilda.Grounder):
    """A grounder for organizations based on ROR."""

    def ground(
        self,
        text: str,
        context: str | None = None,
        organisms: list[str] | None = None,
        namespaces: list[str] | None = None,
    ) -> list[gilda.ScoredMatch]:
        """Ground an organization, and fallback with optional preprocessing."""
        if scored_matches := super().ground(  # type:ignore[no-untyped-call]
            text,
            context=context,
            organisms=organisms,
            namespaces=namespaces,
        ):
            return scored_matches  # type:ignore[no-any-return]

        norm_str = text.removeprefix("The ").replace(",", "")
        return cast(
            list[gilda.ScoredMatch],
            super().ground(  # type:ignore[no-untyped-call]
                norm_str,
                context=context,
                organisms=organisms,
                namespaces=namespaces,
            ),
        )


@lru_cache(1)
def get_ror_grounder(version: str | None = None) -> ssslm.Grounder[curies.NamableReference]:
    """Get a grounder for ROR."""
    return cast(
        ssslm.Grounder[curies.NamableReference],
        pyobo.get_grounder("ror", grounder_cls=RORGrounder, force_process=False, version=version),
    )
