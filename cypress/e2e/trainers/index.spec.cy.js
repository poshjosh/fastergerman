import { Paths } from "../paths"

const givenFirstAndNext = function(selector, triggerNext, onNext) {
  cy.get("#action_start").should("exist").click().then(() => {
    cy.get(selector).should("exist").invoke("text").then(first => {
      if (!first.trim()) {
        throw new Error(`Expected initial ${selector} text, but was empty`)
      }
      triggerNext().then(() => {
        cy.get(selector).should("exist").invoke("text").then(next => {
          if (!next.trim()) {
            throw new Error(`Expected follow-up ${selector} text, but was empty`)
          }
          onNext(first, next)
        })
      })
    })
  })
}

const nextTextShouldBeDifferentOnTrigger = function(selector, triggerNext) {
  givenFirstAndNext(selector, triggerNext, (first, next) => {
    if (next.trim() === first.trim()) {
      throw new Error(`Expected different follow-up ${selector} text, but got the same: '${next}'`)
    }
  })
}

describe('Preposition trainer page game session', () => {
  it('displays question text when start is clicked', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#game_session_question").should("exist").then(questionElement => {
      const startPrompt = questionElement.text();
      cy.get("#action_start").should("exist").click().then(() => {
        cy.hasTextIgnoreSpace("#game_session_question")
        cy.get("#game_session_question").should("not.have.text", startPrompt)
      })
    })
  })
  it('displays question text when pause is clicked', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#game_session_question").should("exist").then(questionElement => {
      const startPrompt = questionElement.text();
      cy.get("#action_start").should("exist").click().then(() => {
        cy.hasTextIgnoreSpace("#game_session_question")
        cy.get("#game_session_question").should("not.have.text", startPrompt)
        cy.get("#action_pause").should("exist").click().then(() => {
          cy.hasTextIgnoreSpace("#game_session_question")
          cy.get("#game_session_question").should("not.have.text", startPrompt)
        })
      })
    })
  })
  it('displays question options when start is clicked', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#action_start").should("exist").click().then(() => {
      cy.get('[name="answer"]').its("length").should("be.greaterThan", 1)
    })
  })
  it('displays pause button when start is clicked', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#action_pause").should("not.exist")
    cy.get("#action_start").should("exist").click().then(() => {
      cy.get("#action_pause").should("exist")
    })
  })
  it('displays start button when pause is clicked', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#action_pause").should("not.exist")
    cy.get("#action_start").should("exist").click().then(() => {
      cy.get("#action_pause").should("exist").click().then(() => {
        cy.get("#action_start").should("exist")
      })
    })
  })
  it('displays no message when resumed after pause', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#action_pause").should("not.exist")
    cy.get("#action_start").should("exist").click().then(() => {
      cy.get("#action_pause").should("exist").click().then(() => {
        cy.get("#action_start").should("exist").click().then(() => {
          cy.hasNoTextIgnoreSpace("#game_session_previous_answer_message")
        })
      })
    })
  })
  it('displays a countdown when start is clicked', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#game_session_countdown").should("exist")
    cy.get("#action_start").should("exist").click().then(() => {
      cy.get("#game_session_countdown").should("exist").invoke("text").then(text => {
        if (!text) {
          throw new Error("Expected count down text, but was empty")
        }
        if (parseInt(text) < 2) {
          throw new Error("Expected value greater than 1, got " + text)
        }
      })
    })
  })
  it('displays a message when an answer is selected', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    cy.get("#action_start").should("exist").click().then(() => {
      cy.hasNoTextIgnoreSpace("#game_session_previous_answer_message")
      cy.get('[name="answer"]').first().should("exist").click().then(() => {
        cy.hasTextIgnoreSpace("#game_session_previous_answer_message")
      })
    })
  })
  it('displays a success message when the correct answer is selected', () => {
    cy.log("TODO - we currently have no way of telling if the answer we selected is correct or not")
  })
  it('displays an error message when the correct answer is selected', () => {
    cy.log("TODO - we currently have no way of telling if the answer we selected is correct or not")
  })
  //@PossibleFlakyTest("Probability of displaying the same question twice depends on the number of available questions")
  it('displays a different question when an answer is selected', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    nextTextShouldBeDifferentOnTrigger("#game_session_question", () => {
      return cy.get('[name="answer"]').first().should("exist").click()
    })
  })
  it('displays a different question when countdown times out', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    const questionDisplayTime = 3
    cy.updateSettings({ "question_display_time": questionDisplayTime })

    nextTextShouldBeDifferentOnTrigger("#game_session_question", () => {
      return cy.wait((questionDisplayTime + 1) * 1000)
    })
  })
  it('displays an updated score when an answer is selected', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    nextTextShouldBeDifferentOnTrigger("#game_session_score", () => {
      return cy.get('[name="answer"]').first().should("exist").click()
    })
  })
  it('displays an updated score when countdown times out', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    const questionDisplayTime = 3
    cy.updateSettings({ "question_display_time": questionDisplayTime })

    nextTextShouldBeDifferentOnTrigger("#game_session_score", () => {
      return cy.wait((questionDisplayTime + 1) * 1000)
    })
  })
  it('displays the right score at the end of the game', () => {
    cy.log(
      "TODO - we have no way of selecting the right answers to lead to game end" +
      "Randomly selecting answers is quite cumbersome giving cypress' async nature")
  })
  it('displays a reset countdown when an answer is selected', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    const questionDisplayTime = 15
    cy.updateSettings({ "question_display_time": questionDisplayTime })

    const triggerNext = () => cy.get('[name="answer"]').first().should("exist").click()
    const onNext = (first, next) => {
      if (parseInt(next) > questionDisplayTime) {
        throw new Error(`Expected number less or equal to ${questionDisplayTime}, got ${next}`)
      }
    }
    givenFirstAndNext("#game_session_countdown", triggerNext, onNext)
  })
  it('displays a reset countdown when countdown times out', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    const questionDisplayTime = 5
    cy.updateSettings({ "question_display_time": questionDisplayTime })

    const triggerNext = () => cy.wait((questionDisplayTime + 1) * 1000)
    const onNext = (first, next) => {
      if (parseInt(next) > questionDisplayTime) {
        throw new Error(`Expected number less or equal to ${questionDisplayTime}, got ${next}`)
      }
    }
    givenFirstAndNext("#game_session_countdown", triggerNext, onNext)
  })
  it('pauses countdown', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    const triggerNext = () => cy.get("#action_pause").should("exist").click()
    const onNext = (first, next) => {
      first = parseInt(first)
      next = parseInt(next)
      if (next - first > 1) {
        throw new Error(`Expected countdown text to change by <= 1, but was more than 1. Before pause: '${first}', after pause: '${next}'`)
      }
    }
    givenFirstAndNext("#game_session_countdown", triggerNext, onNext)
  })
  it('resumes after countdown', () => {
    cy.visit(Paths.url(Paths.prepositionTrainer))
    const selector = "#game_session_countdown"
    const triggerNext = () => cy.get("#action_pause").should("exist").click()
    const onNext = (_, second) => {
      cy.get("#action_start").should("exist").click()
      cy.wait(1500)
      cy.get(selector).should("exist").invoke("text").then(third => {
        if (parseInt(third) >= parseInt(second)) {
          throw new Error(`Expected countdown to resume after pause, but did not. Before pause: '${second}', after pause: '${third}'`)
        }
      })
    }
    givenFirstAndNext(selector, triggerNext, onNext)
  })
})