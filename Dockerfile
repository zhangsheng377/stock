FROM zhangsheng377/stock_base:latest
ENTRYPOINT []

WORKDIR /stock

# ENTRYPOINT ["/stock/docker_cmd.sh"]
CMD ["/bin/bash", "docker_cmd.sh"]
