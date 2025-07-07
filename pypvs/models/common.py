"""Model for common properties of an PVS."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class CommonProperties:
    """Model for common properties of an PVS shared amongst all updaters.

    One set are properties set during probe to share amongst updaters
    and with clients. These should be reset at each probe run.

    More properties can be added, originators should handle reset as needed
    by adding to reset_probe_properties to reset at probe or in a different way
    or leave existing all lifetime.
    """

    # probe properties here, also add to reset_probe_properties
    # shared amongst production updaters, needs reset before probe
    production_fallback_list: list[str] = field(
        default_factory=list[str]
    )  #: Fallback production endpoints for Metered without CT

    # other properties from here, reset by originator

    def reset_probe_properties(self) -> None:
        """Reset common properties that are initialized during probe.

        probe properties are reset at each probe to avoid sticking memories.
        This should exclude common properties set outside of probe
        or controlled by a specific updater, these should be reset at
        different moments by different method by updaters or owner

        reset properties:

            production_fallback_list shared amongst production updaters
        """
        # shared amongst production updaters
        self.production_fallback_list = []

        # shared by
