# Contributing

Change the construction, then derive the assets. Do not redraw or regenerate a logo independently when a canonical source already exists.

1. State the intended change, invariant, and remaining uncertainty. Separate geometric correctness from perception.
2. Edit `source/master.json` for geometry, lettering, placement, colors, or sizes. Keep the L defined once. Repeated glyphs must reuse the same outlines.
3. Run the full build and checks in the README. Preserve the untouched reference PNGs and their hashes. Update the guide and evidence when a claim changes.
4. Inspect only the renderings needed to resolve the changed perceptual claim. Before a reader evaluation, record its question, scope, and decision rule. A model critique is not a human recognition study.
5. Open a pull request with the reason for the change, before/after evidence, executable-check results, and unresolved limits. Do not include private work transcripts, account screenshots, local filesystem paths, or secrets.

Use Conventional Commits for PR titles and squash merge content changes into `main`. Every issue needs a categorization label. Use one closing keyword for each resolved issue and one line per prose paragraph or list item.

Versions follow Semantic Versioning and tags use `vMAJOR.MINOR.PATCH`. A compatible correction is a patch; an additive asset or supported use is a minor version; replacing established geometry, changing the master schema incompatibly, or invalidating existing usage requires a major version. Do not describe a new design as a correction merely to avoid a version boundary.

Changes to deployment targets are separate actions. The files in `github/` document the canonical upload canvases; CI does not upload them or change organization settings.
