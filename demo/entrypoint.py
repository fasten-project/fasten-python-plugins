import argparse
from fasten.plugins.kafka import KafkaPlugin
from random import randint
from time import sleep


class DemoKafkaPlugin(KafkaPlugin):

    def __init__(self, bootstrap_servers, consume_topic, produce_topic,
                 log_topic, error_topic, group_id):
        super().__init__(bootstrap_servers)
        self.consume_topic = consume_topic
        self.produce_topic = produce_topic
        self.log_topic = log_topic
        self.error_topic = error_topic
        self.group_id = group_id
        self.set_consumer()
        self.set_producer()

    def name(self):
        return "DemoKafkaPlugin"

    def description(self):
        return "A Demo Kafka plug-in to check maximum parallelism pattern"

    def version(self):
        return "0.0.1"

    def free_resource(self):
        pass

    def consume(self, record):
        message = self.create_message(record, {"status": "begin"})
        self.emit_message(self.log_topic, message, "begin", "")
        sleep(randint(2, 10))
        if randint(1, 10) <= 1:
            log_message = self.create_message(record, {"status": "failed"})
            self.emit_message(self.log_topic, log_message, "failed", "")
            err_message = self.create_message(record, {"err": "oups"})
            self.emit_message(self.error_topic, err_message, "error", "")
        else:
            log_message = self.create_message(record, {"status": "succeed"})
            self.emit_message(self.log_topic, log_message, "failed", "")
            suc_message = self.create_message(record, {"payload": "yeah"})
            self.emit_message(self.produce_topic, suc_message, "succeed", "")


def get_parser():
    parser = argparse.ArgumentParser(
        "Dummy consumer"
    )
    parser.add_argument('in_topic', type=str, help="Kafka topic to read from.")
    parser.add_argument(
        'out_topic',
        type=str,
        help="Kafka topic to write to."
    )
    parser.add_argument(
        'err_topic',
        type=str,
        help="Kafka topic to write errors to."
    )
    parser.add_argument(
        'log_topic',
        type=str,
        help="Kafka topic to write logs to."
    )
    parser.add_argument(
        'bootstrap_servers',
        type=str,
        help="Kafka servers, comma separated."
    )
    parser.add_argument(
        'group',
        type=str,
        help="Kafka consumer group to which the consumer belongs."
    )
    parser.add_argument(
        'sleep_time',
        type=int,
        help="Time to sleep in between each scrape (in sec)."
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    in_topic = args.in_topic
    out_topic = args.out_topic
    err_topic = args.err_topic
    log_topic = args.log_topic
    bootstrap_servers = args.bootstrap_servers
    group = args.group
    sleep_time = args.sleep_time

    plugin = DemoKafkaPlugin(bootstrap_servers, in_topic, out_topic, log_topic,
                             err_topic, group)

    # Run forever
    while True:
        plugin.consume_messages()
        sleep(sleep_time)


if __name__ == "__main__":
    main()
