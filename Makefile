IMAGE_NAME := seg-annotator
TAG := 0.0.1

.PHONY: build
build:
ifeq ($(NO_CACHE), true)
		$(eval BUILD_ARG := $(BUILD_ARG) --no-cache)
endif
	docker build \
	$(BUILD_ARG) \
	-t ${IMAGE_NAME}:${TAG} \
	.

.PHONY: run
run:
	xhost +si:localuser:root
	docker run -it --rm \
	-e DISPLAY=${DISPLAY} \
	-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
	--name ${IMAGE_NAME} \
	-v ./:/app:rw \
	${IMAGE_NAME}:${TAG}
