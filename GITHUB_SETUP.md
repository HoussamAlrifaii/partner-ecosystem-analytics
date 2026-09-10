# GitHub setup and phase history

Connected account checked: HoussamAlrifaii. Current connector actions can change existing repositories but do not include repository creation. No project repository has been created or pushed by this release. This is a capability limitation, not a new permission request.

Create an empty repository named partner-ecosystem-intelligence under the intended account. Do not initialize a README, license or gitignore because this package already has history. Public is suitable once you have reviewed the synthetic source and are ready to share it; private is fine while learning. Send its URL in the chat so the connected workflow can continue against that explicit destination.

## Restore the phase commits locally

The ZIP contains the complete source folder plus phase01-history.bundle. You can read/run the extracted source directly. To get a working checkout with the existing commits, clone the bundle into a DIFFERENT folder beside the extracted source:

~~~bash
git clone phase01-history.bundle partner-ecosystem-intelligence-git
cd partner-ecosystem-intelligence-git
git remote remove origin
git remote add origin \
  https://github.com/HoussamAlrifaii/partner-ecosystem-intelligence.git
git push -u origin main
~~~

Run the push only after the empty repository exists and your local GitHub authentication is configured. No token belongs in the source or chat. If the destination has content, inspect and integrate its history first; never force-push over existing work.

The initial local commits identify Portfolio Build Assistant, making the authorship of generated scaffolding explicit. Configure your own preferred GitHub name and private/no-reply email before your next learning commit. Do not copy an arbitrary email address from this guide.

## Every later phase

Read the explanation, make the planned changes, run the relevant checks, update the runbook and validation evidence, review git diff, stage only intended files, then make a descriptive phase commit and push. Example after phase 03 is actually complete:

~~~bash
git status
git diff
git add powerbi docs PROJECT_RUNBOOK.md README.md
git commit -m "feat(phase-03): validate Power BI model and report"
git push
~~~

PBIX files are ignored initially. Prefer committing the text project format if supported and validated in your Desktop version; otherwise distribute the reviewed PBIX as a release asset and link it from the README. Review its contents before publishing, including model data. Do not commit generated datasets, environments, secrets or unreviewed employer files.
