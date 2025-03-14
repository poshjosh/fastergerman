import { Paths } from "../paths"

describe('Preposition trainer page settings', () => {
  it('has default values that cause no error', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#settings_tab").should("exist").click().then(() => {
      cy.get("#action_update").should("exist").click().then(() => {
        cy.get("#page_error").should("not.have.text")
      })
    })
  })
  it('shows error if out of range questions selected', () => {
    const settings = {
      "number_of_choices": 2,
      "question_display_time": 2,
      "max_consecutively_correct": 2,
      // a number larger than the max available question usually less than 500.
      // 999 is the max the input allows for now.
      "start_at_question_number": 999,
      "max_number_of_questions": 2,
      "display_translation": false,
    }
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.setSettings(settings, () => {
      cy.get("#action_update").should("exist").click().then(() => {
        cy.get("#page_error").invoke("text").then(text => {
          if (!text) {
            throw new Error("Should have error. But found: " + text)
          }
        })
      })
    })
  })
  it('is hidden on page load', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#settings").should("have.css", "display", "none")
  })
  it('is displayed when settings tab clicked', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#settings_tab").should("exist").click().then(() => {
      cy.get("#settings").should("have.css", "display", "block")
    })
  })
  it('is hidden when settings tab clicked again', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#settings_tab").should("exist").click().then(() => {
      cy.get("#settings_tab").click().then(() => {
        cy.get("#settings").should("have.css", "display", "none")
      })
    })
  })
  it('submits specified values', () => {
    const settings = {
      "number_of_choices": 2,
      "question_display_time": 2,
      "max_consecutively_correct": 2,
      "start_at_question_number": 2,
      "max_number_of_questions": 2,
      "display_translation": false,
    }
    cy.updateSettings(settings)
  })
})