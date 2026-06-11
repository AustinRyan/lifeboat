---
product: "Microsoft Publisher"
tagline: "Microsoft's desktop-publishing app for flyers, newsletters, and bulletins since 1991"
status: sinking
announced: "2024-02-15"
deadline: "2026-10-13"
sourceUrl: "https://support.microsoft.com/en-us/office/microsoft-publisher-will-no-longer-be-supported-after-october-2026-ee6302a2-4bc7-4841-babf-8e9be3acbfd7"
alternatives:
  - name: "Affinity Publisher"
    url: "https://affinity.serif.com/en-us/publisher/"
    pitch: "The closest professional replacement: real page-layout tooling, one-time purchase, no subscription. Imports the PDFs you export from Publisher."
    affiliateKey: "affinity"
  - name: "Canva"
    url: "https://www.canva.com"
    pitch: "Easiest landing spot for non-designers — browser-based, thousands of newsletter/flyer templates, free tier. Rebuild from template rather than importing."
    affiliateKey: "canva"
  - name: "Scribus"
    url: "https://www.scribus.net"
    pitch: "Free and open source desktop publishing. Steeper learning curve, but zero cost and no vendor can ever sunset it on you."
  - name: "Adobe InDesign"
    url: "https://www.adobe.com/products/indesign.html"
    pitch: "The industry standard, if you're going professional anyway. Subscription pricing; overkill for church bulletins."
    affiliateKey: "adobe"
---

## What happened

Microsoft [announced on February 15, 2024](https://support.microsoft.com/en-us/office/microsoft-publisher-will-no-longer-be-supported-after-october-2026-ee6302a2-4bc7-4841-babf-8e9be3acbfd7)
that Publisher retires on **October 13, 2026**. After that date it is removed
from Microsoft 365 — subscribers can no longer install it, open it, or edit
`.pub` files with it. If you own a perpetual (one-time-purchase) copy, the app
keeps launching, but with no security patches or support, and Microsoft
recommends converting your files regardless: their guidance is to **convert
before October 1, 2026**.

The dangerous part isn't losing the app — it's the thirty years of `.pub`
files that almost nothing else on Earth can open.

## Do this before October 1, 2026

1. **Inventory every `.pub` file you have.** Search your drives, OneDrive,
   SharePoint, and that one church/office PC: `*.pub`.
2. **Batch-convert everything to PDF now** (script below). PDF preserves the
   exact layout and every modern tool can read it.
3. **For documents you still actively edit**, also produce an editable copy:
   open the exported PDF in Word (File → Open → select the PDF) — layout-heavy
   documents will need cleanup, so do this while you can still compare against
   the original.
4. **Don't uninstall Publisher yet.** Keep it until every file is converted
   and spot-checked.

## Migrating your data

On any PC with Publisher installed, this PowerShell script converts every
`.pub` under a folder to PDF in place — point `$root` at your documents folder
and run it in a regular PowerShell window:

```powershell
$root = "C:\Users\you\Documents"
$publisher = New-Object -ComObject Publisher.Application
Get-ChildItem -Path $root -Filter *.pub -Recurse | ForEach-Object {
    $doc = $publisher.Open($_.FullName)
    $pdf = [System.IO.Path]::ChangeExtension($_.FullName, ".pdf")
    $doc.ExportAsFixedFormat(2, $pdf)   # 2 = PDF
    $doc.Close()
    Write-Host "converted $($_.FullName)"
}
$publisher.Quit()
```

If you no longer have Publisher anywhere, **LibreOffice Draw** (free) can open
most `.pub` files directly — quality varies with document complexity, but it's
the best `.pub` reader that isn't Publisher.

Where to land: **Affinity Publisher** if you do real layout work and want to
own your software; **Canva** if you mostly made flyers and newsletters from
templates and want the least friction; **Scribus** if budget is zero.
