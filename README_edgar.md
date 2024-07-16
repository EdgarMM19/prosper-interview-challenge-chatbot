To run make what is in the original README.md, add openai and elevenlabs keys and turn on the speakers.

---

# TIME
1h30 reading documentation + setting up

1h30 understanding how to access responses (first commit)

5' 2nd commit

1h30 3rd commit. Basic flow done.

1h 4th commit. End session (had some problems, not very nice solution(?), fixed in two commits below)

30' 5th commit. Error logger and confirmation for appointment function.

20' 6th commit. End session with frames.

1h30 7th commit. Voice. Tried to do with pipecat but did not succeed. Finished using elevenlabs api directly (5 minutes lol). A bit laggy.

About ~7 hours of coding. ~2 hours of reading either not logged in previous times or for the questions below. ~1 hour wrapping things up. Some time thinking about the problem without the computer in front or testing the chat a bit.

---

# Accuracy

If deployed. I think that a good metric would be: #appointments made / #cost of openAI API.

If not deployed. This is a _very difficult_ task to automatize. I would try to create a bunch of cases with corner-cases and manually test them assessing how well does the chatbot respond. Alternatively you could make _another_ chatbot to run this cases versus the first chatbot, but would be more involved.

---

# Improve accuracy

1. While doing the test I realized that tweaking the "internal" prompts made a huge difference in how exact the chatbot did its tasks, so that would be an important must in order to optimize the chatbot. Both in the first prompt as in the states prompts.

2. Indeed, having a good set of states with the flow between them is important. Still, there is a tension between making a lot of states for every possible case and keeping the states general enough so the bot generalizes well in all odd cases that an user can produce.

3. Making sure the chat responds quickly. At the moment the audio is _slightly_ slow to start. Making sure the chat communicates fast and clearly is important. I guess that an slow chat makes people annoyed.



