# Tech Brief Codex Skill

Repository source for the Codex skill that publishes the KAIST Daily Tech Brief.

Install or refresh the skill on Windows:

```powershell
Set-Location <techbrief-repo-root>
.\install-windows.ps1 -InstallPlaywright
```

The install script copies `.codex\skills\tech-news-daily` into `%USERPROFILE%\.codex\skills\tech-news-daily` and validates the skill.
