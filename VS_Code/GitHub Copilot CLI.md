[GitHub Copilot CLI · GitHub](https://github.com/features/copilot/cli)

[GitHub - github/copilot-cli: GitHub Copilot CLI brings the power of Copilot coding agent directly to your terminal.](https://github.com/github/copilot-cli?tab=readme-ov-file#-getting-started)

### Prerequisites

[](https://github.com/github/copilot-cli?tab=readme-ov-file#prerequisites)

- **Node.js** v22 or higher
- **npm** v10 or higher
- (On Windows) **PowerShell** v6 or higher
- An **active Copilot subscription**. See [Copilot plans](https://github.com/features/copilot/plans?ref_cta=Copilot+plans+signup&ref_loc=install-copilot-cli&ref_page=docs).

If you have access to GitHub Copilot via your organization of enterprise, you cannot use GitHub Copilot CLI if your organization owner or enterprise administrator has disabled it in the organization or enterprise settings. See [Managing policies and features for GitHub Copilot in your organization](http://docs.github.com/copilot/managing-copilot/managing-github-copilot-in-your-organization/managing-github-copilot-features-in-your-organization/managing-policies-for-copilot-in-your-organization) for more information.

### Installation

[](https://github.com/github/copilot-cli?tab=readme-ov-file#installation)

Install globally with npm:

```shell
npm install -g @github/copilot
```

### Launching the CLI

[](https://github.com/github/copilot-cli?tab=readme-ov-file#launching-the-cli)

```shell
copilot
```

On first launch, you'll be greeted with our adorable animated banner! If you'd like to see this banner again, launch `copilot` with the `--banner` flag.

If you're not currently logged in to GitHub, you'll be prompted to use the `/login` slash command. Enter this command and follow the on-screen instructions to authenticate.

#### Authenticate with a Personal Access Token (PAT)

[](https://github.com/github/copilot-cli?tab=readme-ov-file#authenticate-with-a-personal-access-token-pat)

You can also authenticate using a fine-graned PAT with the "Copilot Rrequests" permission enabled.

1. Visit [https://github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)
2. Under "Permissions," click "add permissions" and select "Copilot Requests"
3. Generate your token
4. Add the token to your environment via the environment variable `GH_TOKEN` or `GITHUB_TOKEN` (in order of precedence)