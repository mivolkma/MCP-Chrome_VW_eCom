# BTO Testcharta – kompakte Steps (35 Szenarien)

Quelle: prompts/testdata/BTO-testcharta.json

Hinweise:
- Keine Secrets/Tokens in Logs oder Dateien schreiben.
- Bekannter Chrome-Dialog: Bei Domain-Endung `.eu` Credentials erneut eingeben und fortfahren; bei `.io` Dialog schließen.
- E-Mail für Tests: test@test.de
- Letztes Szenario wird übersprungen (derzeit nur via VPN erreichbar).

## 1. eCom CTA_Configurator

**Beschreibung**
Verify that:
- a CTA for starting the eCommerce journey is available in the summary page of the configurator feature app.
- the eCom CTA is active and clickable.
- clicking on the eCom CTA starts the

**Testcases**
- OH-eCom-BTO-01: Verify that:
  - Open URL - value=/konfigurator.html/__app1/id4-gtx-individualausstattung/
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 2. eCom page

**Beschreibung**
Verify that:
- the eCom CTA opens a new page and starts with the personal data tab.
- the eCom page displays a tab slider, highlighted personal data tab, a price box, the content of the current eCom j

**Testcases**
- OH-eCom-BTO-02: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 3. eCom page
The tab slider

**Beschreibung**
Verify that:
- the tab slider displays many tabs that cover all eCom journey steps.
- the tabs that have not been accessed yet appear deactivated.
- the slider has a right and left functioning sliding

**Testcases**
- OH-eCom-BTO-03: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 4. eCom page
The price box

**Beschreibung**
Verify that:
- the price box is displayed at the right side of the eCom page.
- the correct information has been passed on to the eCommerce feature app and is displayed in the price box, for example t

**Testcases**
- OH-eCom-BTO-04: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 5. eCom page
The price box

**Beschreibung**
Verify that:
- a clickable link is displayed to enable the editing of the fincing parameters.
- clicking on the mentioned link opens the fincing layer.
- changing the fincing parameters is possi

**Testcases**
- OH-eCom-BTO-05: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 6. eCom page
The Sticky bar

**Beschreibung**
Verify that:
- the sticky bar is displayed at the bottom of the viewport and sticks to it while scrolling the eCom page down until the footer section is accessed.
- the Next Step CTA is displayed on t

**Testcases**
- OH-eCom-BTO-06: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 7. eCom Page
The Disclaimers

**Beschreibung**
Verify that:
- two disclaimer references are displayed next to the total price and the total leasing rate.
- Corresponding disclaimer texts are displayed at the bottom of the eCom page.
- when the sum

**Testcases**
- OH-eCom-BTO-07: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 8. eCom journey_The personal data tab

**Beschreibung**
Verify that:
- the personal data tab has a headline and a copy text requesting the user to enter the personal data.
- specific dropdowns and input fields are displayed.
- the user can use all the drop

**Testcases**
- OH-eCom-BTO-08: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 9. eCom journey_The personal data tab

**Beschreibung**
Verify that:
- proceeding to the next eCom step is only possible when all mandatory information has been provided.
- clicking on the Next Step CTA leads to the Volkswagen partner step.

**Testcases**
- OH-eCom-BTO-09: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 10. eCom journey_The Volkswagen partner tab

**Beschreibung**
Verify that:
- the content of the Volkswagen partner tab can be accessed.
- a headline and text are displayed.

**Testcases**
- OH-eCom-BTO-10: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 11. eCom journey_The Volkswagen partner
tab-Input field

**Beschreibung**
Verify that:
- a search input  field for searching dealers is displayed.
- Locate Me functionality is visible

**Testcases**
- OH-eCom-BTO-11: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 12. eCom journey_The Volkswagen partner
tab-Dealer searching

**Beschreibung**
Verify that:
- searching by cities or postal codes shows many corresponding results.
- the location of the selected dealer is displayed on a map which can be activated in the first visit.

**Testcases**
- OH-eCom-BTO-12: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 13. eCom journey_The Volkswagen partner
tab-Dealer selection

**Beschreibung**
Verify that:
- every shown result can be selected.
- clicking on the Next Step CTA leads to the Pick up step.

**Testcases**
- OH-eCom-BTO-13: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 14. eCom journey_The Pick up tab

**Beschreibung**
Verify that:
- the content of the Pick up tab can be accessed.
- specific headline and copy text are displayed.

**Testcases**
- OH-eCom-BTO-14: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 15. eCom journey_The Pick up tab
Pick up options

**Beschreibung**
Verify that:
- The dealer selected in the previous step and further options for picking up the car will be displayed.
- Clicking on the ‘More information’ link opens a corresponding information layer.

**Testcases**
- OH-eCom-BTO-15: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 16. eCom journey_The Pick up tab
Transfer costs

**Beschreibung**
Verify that:
- every pick up option has specific transfer costs which effects the total leasing rate.

**Testcases**
- OH-eCom-BTO-16: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 17. eCom journey_The Pick up tab
Pick up selection

**Beschreibung**
Verify that:
- all the shown options are selectable.
- By clicking on the CTA ‘Next Step’ you will be taken to the step ‘Summary’ only if a pick-up option has been selected.

**Testcases**
- OH-eCom-BTO-17: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 18. eCom journey_The Summary tab

**Beschreibung**
Verify that:
- the content of the Summary tab can be accessed.
- a specific headline is displayed.

**Testcases**
- OH-eCom-BTO-18: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 19. eCom journey_The Summary tab
Personal information

**Beschreibung**
Verify that:
- some provided personal data is shown.
- the wished contract is shown under the corresponding section.

**Testcases**
- OH-eCom-BTO-19: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 20. eCom journey_The Summary tab
The offerer

**Beschreibung**
Verify that:
- the offerer is shown under the corresponding section.
- a clickable info icon is displayed next to the offere which opens a corresponding info layer if clicked on.
- the info layer can

**Testcases**
- OH-eCom-BTO-20: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 21. eCom journey_The Summary tab
The dealer

**Beschreibung**
Verify that:
- the selected dealer is shown under the corresponding section.
- the dealer address, telephone number, website, and email address are shown.
- the following text message is also shown un

**Testcases**
- OH-eCom-BTO-21: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 22. eCom journey_The Summary tab
The pick up location

**Beschreibung**
Verify that:
- the selected pick up location is shown under the corresponding section.
- a non-binding delivery date is shown.

**Testcases**
- OH-eCom-BTO-22: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 23. eCom journey_The Summary tab
The selected vehicle

**Beschreibung**
Verify that:
- the selected vehicle information is shown under the corresponding section.
- the full name of the selected vehicle is shown.

**Testcases**
- OH-eCom-BTO-23: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 24. eCom journey_The Summary tab
Energy and Emissions Specifications

**Beschreibung**
Verify that:
- the consumption, emission, and the co2 efficiency information is displayed.
- a disclaimer reference is displayed next to the co2 class which refer to a corresponding disclaimer text at

**Testcases**
- OH-eCom-BTO-24: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 25. eCom journey_The Summary tab
ENVKV label

**Beschreibung**
Verify that:
- a clickable link is show.
- clicking on the link opens a layer showing the ENVKV label.
- the ENVKV layer can be closed by clicking on the close button or the shim.

**Testcases**
- OH-eCom-BTO-25: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 26. eCom journey_The Summary tab
Expanding and collapsing the section

**Beschreibung**
Verify that:
- a dropdown button is shown.
- clicking on the dropdown button expands the selected vehicle section and clicking on it again collapses it.
- the expantion shows more vehicle information,

**Testcases**
- OH-eCom-BTO-26: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 27. eCom journey_The Summary tab
The tire labels

**Beschreibung**
Verify that:
- clicking on the tire label link opens the corresponding tire label layer.
- related vehicle tire labels are displayed in the layer (svg graphics).
- the layer can be closed by clicking

**Testcases**
- OH-eCom-BTO-27: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 28. eCom journey_The Summary tab
The product safty information

**Beschreibung**
Verify that:
- clicking on the product safty information link leads to a separate page.

**Testcases**
- OH-eCom-BTO-28: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 29. eCom journey_The Summary tab
The manufacturer

**Beschreibung**
Verify that:
- the manufacturer is shown under the corresponding section.
- the address and the email address of the manufacturer are shown under this section.

**Testcases**
- OH-eCom-BTO-29: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 30. eCom journey_The Summary tab
Proceeding the journey

**Beschreibung**
Verify that:
- contract documents are shown in some cases(needs to be investigated more).
- selectable additional services are shown.
- clicking on the Next Step CTA leads to the Thank you step.

**Testcases**
- OH-eCom-BTO-30: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 31. eCom journey_Thank You tab

**Beschreibung**
Verify that:
- the content of the "Thank You" tab can be accessed.
- a "Thank You" text message is displayed for the user for being interrested.

**Testcases**
- OH-eCom-BTO-31: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 32. eCom journey_Thank You tab
Confirmation email

**Beschreibung**
Verify that:
- the user is informed about a confirmation email that has been sent.

**Testcases**
- OH-eCom-BTO-32: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 33. eCom journey_Thank You tab
Selection overivew

**Beschreibung**
Verify that:
- an overview of selected options is shown.

**Testcases**
- OH-eCom-BTO-33: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 34. Proceeding the journey to the FSAG

**Beschreibung**
Verify that:
- a Next Step CTA is displayed.

**Testcases**
- OH-eCom-BTO-34: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## 35. Proceeding the journey to the FSAG

**Beschreibung**
Verify that:
'- clicking on the Next Step CTA leads to the corresponding FSAG page.

**Testcases**
- OH-eCom-BTS-35: Verify that:
  - Open URL
  - Verify UI elements - testid=placeholder-testid

**Negative Tests (Auszug)**
- Verify error when mandatory fields are empty
- Verify error for invalid email format

## Übersprungen (VPN)
- (ohne Titel)
