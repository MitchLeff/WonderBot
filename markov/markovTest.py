import markovify

# Get raw text as string.
with open("C:\\Users\\ml185201\\Desktop\\markov\\corpus.txt", "r") as f:
    text = f.read()

# Build the model.
text_model = markovify.NewlineText(text)

# Print five randomly-generated sentences
for i in range(5):
    print(text_model.make_sentence(test_output=False))
