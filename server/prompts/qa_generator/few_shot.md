<!-- Technique 3: Few-shot.
     Instead of rules, the model gets examples: single questions on C++, JavaScript and
     software engineering (each with its topic, level and type), then one complete example
     from input to answer. It should copy the style: concrete, spoken, fitting the level.
     The complete example is for a Junior Frontend Developer, so it differs from the test
     case of the Prompt Lab. -->
Write 5 interview questions for the role and level the user gives you. Write them in the same style as the examples below.

### Example questions

Topic: C++ · Level: Senior · Type: technical
"A long-running C++ service slowly uses more and more memory. How do you find the leak, and how would RAII or smart pointers have prevented it?"

Topic: JavaScript · Level: Junior · Type: technical
"What is the difference between let, const and var in JavaScript, and when do you use which?"

Topic: Software engineering · Level: Mid · Type: practice
"You have to change code that has no tests. How do you make sure you don't break anything?"

Topic: Teamwork · Level: any · Type: behavioral
"Tell me about a technical disagreement with a colleague. How did you solve it?"

### Complete example

Input:
Role: Frontend Developer
Level: Junior

Answer:
{"questions": [
  "What is the difference between let, const and var in JavaScript, and when do you use which?",
  "How do you make a web page look good on both a phone and a large screen?",
  "What happens in a React component when its state changes?",
  "A button on the page does nothing when you click it. How do you find out why?",
  "Tell me about a project where you learned a new tool quickly. How did you go about it?"
]}

### Your task

Reply with JSON only, in exactly this format:
{"questions": ["question 1", "question 2", "question 3", "question 4", "question 5"]}
