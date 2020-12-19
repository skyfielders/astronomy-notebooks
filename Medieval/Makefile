
planets := Mercury Venus Mars Jupiter Saturn
planet_outputs := $(patsubst %, fit_%.png, $(planets))

all: $(planet_outputs)

$(planet_outputs): fit_%.png: fitting.py
	python fitting.py $*
