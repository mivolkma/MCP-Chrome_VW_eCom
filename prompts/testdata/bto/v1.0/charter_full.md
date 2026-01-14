# BTO Checkout – extrahierte Testschritte (aus Excel)

Quelle: Testcharter - eCom-BTO_10.10.2025.xlsx

Hinweis: Diese Datei enthält nur Testschritt-Texte/URLs aus der Excel.

## eCom-BTO-Configurator

- [ ] **OH-eCom-BTO-01 – eCom CTA_Configurator**
  - Ziel: Verify that:
- a CTA for starting the eCommerce journey is available in the summary page of the configurator feature app.
- the eCom CTA is active and clickable.
- clicking on the eCom CTA starts the corresponding eCommerce journey.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-02 – eCom page**
  - Ziel: Verify that:
- the eCom CTA opens a new page and starts with the personal data tab.
- the eCom page displays a tab slider, highlighted personal data tab, a price box, the content of the current eCom journey step, the sticky bar and the Next Step CTA, and the price and leasing offer disclaimers at the bottom of it.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-03 – eCom page
The tab slider**
  - Ziel: Verify that:
- the tab slider displays many tabs that cover all eCom journey steps.
- the tabs that have not been accessed yet appear deactivated.
- the slider has a right and left functioning sliding arrows.
  - TA: yes | Status: Completed

## eCom-BTO-Price Box

- [ ] **OH-eCom-BTO-04 – eCom page
The price box**
  - Ziel: Verify that:
- the price box is displayed at the right side of the eCom page.
- the correct information has been passed on to the eCommerce feature app and is displayed in the price box, for example the car's name, the selected financing parameters, and the total price.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-05 – eCom page
The price box**
  - Ziel: Verify that:
- a clickable link is displayed to enable the editing of the financing parameters.
- clicking on the mentioned link opens the financing layer.
- changing the financing parameters is possible.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-06 – eCom page
The Sticky bar**
  - Ziel: Verify that:
- the sticky bar is displayed at the bottom of the viewport and sticks to it while scrolling the eCom page down until the footer section is accessed.
- the Next Step CTA is displayed on the sticky bar.
- clicking the Next Step CTA always leads to the next step when the current step is completed.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-07 – eCom Page
The Disclaimers**
  - Ziel: Verify that:
- two disclaimer references are displayed next to the total price and the total leasing rate.
- Corresponding disclaimer texts are displayed at the bottom of the eCom page.
- when the summary step is accessed, the CO2 class disclaimer reference and text is also displayed.
  - TA: yes | Status: Completed

## eCom-BTO-Personal Data

- [ ] **OH-eCom-BTO-08 – eCom journey_The personal data tab**
  - Ziel: Verify that:
- the personal data tab has a headline and a copy text requesting the user to enter the personal data.
- specific dropdowns and input fields are displayed.
- the user can use all the dropdowns and input field to enter the personal data.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-09 – eCom journey_The personal data tab**
  - Ziel: Verify that:
- proceeding to the next eCom step is only possible when all mandatory information has been provided.
- clicking on the Next Step CTA leads to the Volkswagen partner step.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-10 – eCom journey_The Volkswagen partner tab**
  - Ziel: Verify that:
- the content of the Volkswagen partner tab can be accessed.
- a headline and text are displayed.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-11 – eCom journey_The Volkswagen partner
tab-Input field**
  - Ziel: Verify that:
- a search input  field for searching dealers is displayed.
- Locate Me functionality is visible
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-12 – eCom journey_The Volkswagen partner
tab-Dealer searching**
  - Ziel: Verify that:
- searching by cities or postal codes shows many corresponding results.
- the location of the selected dealer is displayed on a map which can be activated in the first visit.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-13 – eCom journey_The Volkswagen partner
tab-Dealer selection**
  - Ziel: Verify that:
- every shown result can be selected.
- clicking on the Next Step CTA leads to the Pick up step.
  - TA: yes | Status: Completed

## eCom-BTO-Pick Up

- [ ] **OH-eCom-BTO-14 – eCom journey_The Pick up tab**
  - Ziel: Verify that:
- the content of the Pick up tab can be accessed.
- specific headline and copy text are displayed.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-15 – eCom journey_The Pick up tab
Pick up options**
  - Ziel: Verify that:
- The dealer selected in the previous step and further options for picking up the car will be displayed.
- Clicking on the ‘More information’ link opens a corresponding information layer.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-16 – eCom journey_The Pick up tab
Transfer costs**
  - Ziel: Verify that:
- every pick up option has specific transfer costs which effects the total leasing rate.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-17 – eCom journey_The Pick up tab
Pick up selection**
  - Ziel: Verify that:
- all the shown options are selectable.
- By clicking on the CTA ‘Next Step’ you will be taken to the step ‘Summary’ only if a pick-up option has been selected.
  - TA: yes | Status: Completed

## eCom-BTO-Summary

- [ ] **OH-eCom-BTO-18 – eCom journey_The Summary tab**
  - Ziel: Verify that:
- the content of the Summary tab can be accessed.
- a specific headline is displayed.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-19 – eCom journey_The Summary tab
Personal information**
  - Ziel: Verify that:
- some provided personal data is shown.
- the wished contract is shown under the corresponding section.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-20 – eCom journey_The Summary tab
The offerer**
  - Ziel: Verify that:
- the offerer is shown under the corresponding section.
- a clickable info icon is displayed next to the offere which opens a corresponding info layer if clicked on.
- the info layer can be closed by clicking on the close button.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-21 – eCom journey_The Summary tab
The dealer**
  - Ziel: Verify that:
- the selected dealer is shown under the corresponding section.
- the dealer address, telephone number, website, and email address are shown.
- the following text message is also shown under the dealer section. "The Volkswagen partner you select will receive access to your order information as part of managing your order process."
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-22 – eCom journey_The Summary tab
The pick up location**
  - Ziel: Verify that:
- the selected pick up location is shown under the corresponding section.
- a non-binding delivery date is shown.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-23 – eCom journey_The Summary tab
The selected vehicle**
  - Ziel: Verify that:
- the selected vehicle information is shown under the corresponding section.
- the full name of the selected vehicle is shown.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-24 – eCom journey_The Summary tab
Energy and Emissions Specifications**
  - Ziel: Verify that:
- the consumption, emission, and the co2 efficiency information is displayed.
- a disclaimer reference is displayed next to the co2 class which refer to a corresponding disclaimer text at the bottom of the eCom page.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-25 – eCom journey_The Summary tab
ENVKV label**
  - Ziel: Verify that:
- a clickable link is show.
- clicking on the link opens a layer showing the ENVKV label.
- the ENVKV layer can be closed by clicking on the close button or the shim.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-26 – eCom journey_The Summary tab
Expanding and collapsing the section**
  - Ziel: Verify that:
- a dropdown button is shown.
- clicking on the dropdown button expands the selected vehicle section and clicking on it again collapses it.
- the expantion shows more vehicle information, tire label link, product safty information link and the special equipment if selected.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-27 – eCom journey_The Summary tab
The tire labels**
  - Ziel: Verify that:
- clicking on the tire label link opens the corresponding tire label layer.
- related vehicle tire labels are displayed in the layer (svg graphics).
- the layer can be closed by clicking on the close button or the shim.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-28 – eCom journey_The Summary tab
The product safty information**
  - Ziel: Verify that:
- clicking on the product safty information link leads to a separate page.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-29 – eCom journey_The Summary tab
The manufacturer**
  - Ziel: Verify that:
- the manufacturer is shown under the corresponding section.
- the address and the email address of the manufacturer are shown under this section.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-30 – eCom journey_The Summary tab
Proceeding the journey**
  - Ziel: Verify that:
- contract documents are shown in some cases(needs to be investigated more).
- selectable additional services are shown.
- clicking on the Next Step CTA leads to the Thank you step.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-31 – eCom journey_Thank You tab**
  - Ziel: Verify that:
- the content of the "Thank You" tab can be accessed.
- a "Thank You" text message is displayed for the user for being interrested.
  - TA: yes | Status: Completed

## eCom-BTO-Thank You

- [ ] **OH-eCom-BTO-32 – eCom journey_Thank You tab
Confirmation email**
  - Ziel: Verify that:
- the user is informed about a confirmation email that has been sent.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTO-33 – eCom journey_Thank You tab
Selection overivew**
  - Ziel: Verify that:
- an overview of selected options is shown.
  - TA: yes | Status: Completed

## eCom-BTO-FSAG

- [ ] **OH-eCom-BTO-34 – Proceeding the journey to the FSAG**
  - Ziel: Verify that:
- a Next Step CTA is displayed.
  - TA: yes | Status: Completed
- [ ] **OH-eCom-BTS-35 – Proceeding the journey to the FSAG**
  - Ziel: Verify that:
'- clicking on the Next Step CTA leads to the corresponding FSAG page.
  - TA: No | Status:
