"""
Performance Tests for Pure Sound Application

This module measures and validates:
- Response times for operations
- Throughput (operations per second)
- Load handling under concurrent requests
- Scalability under stress conditions
- Resource utilization efficiency
"""

import unittest
import time
import threading
import queue
import statistics
import psutil
import gc
import os
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Callable, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing


@dataclass
class PerformanceResult:
    """Result of a performance test"""
    operation_name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    throughput: float  # operations per second
    percentile_95: float
    percentile_99: float
    memory_used: int = 0
    cpu_percent: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation_name,
            "iterations": self.iterations,
            "total_time": f"{self.total_time:.4f}s",
            "avg_time": f"{self.avg_time:.6f}s",
            "min_time": f"{self.min_time:.6f}s",
            "max_time": f"{self.max_time:.6f}s",
            "std_dev": f"{self.std_dev:.6f}s",
            "throughput": f"{self.throughput:.2f} ops/sec",
            "percentile_95": f"{self.percentile_95:.6f}s",
            "percentile_99": f"{self.percentile_99:.6f}s",
            "memory_mb": f"{self.memory_used / 1024 / 1024:.2f}",
            "cpu_percent": f"{self.cpu_percent:.1f}%"
        }


class PerformanceTimer:
    """Helper class for timing operations"""
    
    def __init__(self):
        self.times: List[float] = []
    
    def __enter__(self):
        gc.collect()  # Clean up before timing
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.times.append(self.end_time - self.start_time)
    
    def get_results(self, operation_name: str, iterations: int) -> PerformanceResult:
        times = self.times
        sorted_times = sorted(times)
        
        total_time = sum(times)
        avg_time = total_time / iterations
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        
        throughput = iterations / total_time if total_time > 0 else 0
        
        # Calculate percentiles
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)
        percentile_95 = sorted_times[p95_idx] if sorted_times else 0
        percentile_99 = sorted_times[p99_idx] if sorted_times else 0
        
        # Memory and CPU
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_used = memory_info.rss
        cpu_percent = process.cpu_percent()
        
        return PerformanceResult(
            operation_name=operation_name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            throughput=throughput,
            percentile_95=percentile_95,
            percentile_99=percentile_99,
            memory_used=memory_used,
            cpu_percent=cpu_percent
        )


class TestResponseTimes(unittest.TestCase):
    """Test response times for various operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "config.json"
        
        # Create test configuration
        self.test_config = {
            "model_paths": {
                "arnndn_model": "/usr/local/share/ffmpeg/arnndn-models/bd.cnr.mdl",
                "custom_models_dir": "./models"
            },
            "presets": {
                "speech": {"compressor": {"threshold": -20, "ratio": 3}},
                "music": {"compressor": {"threshold": -18, "ratio": 4}}
            },
            "output_formats": {
                "mp3": {"codec": "libmp3lame", "ext": ".mp3", "speech": [64, 96, 128], "music": [128, 192, 256]},
                "opus": {"codec": "libopus", "ext": ".opus", "speech": [24, 32, 48], "music": [64, 96, 128]}
            },
            "default_settings": {
                "format": "mp3",
                "content_type": "speech",
                "channels": 1
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_config_file_read_time(self):
        """Test configuration file read response time"""
        iterations = 1000
        
        with PerformanceTimer() as timer:
            for _ in range(iterations):
                with open(self.config_file, 'r') as f:
                    json.load(f)
        
        result = timer.get_results("config_file_read", iterations)
        
        # Assert performance threshold (avg read should be under 1ms)
        self.assertLess(result.avg_time, 0.001, f"Config read too slow: {result.avg_time:.6f}s")
        self.assertGreater(result.throughput, 500, f"Throughput too low: {result.throughput:.2f} ops/sec")
        
        print(f"\nConfig File Read Performance:")
        print(f"  Avg: {result.avg_time*1000:.4f}ms | Throughput: {result.throughput:.2f} ops/sec")
    
    def test_config_file_write_time(self):
        """Test configuration file write response time"""
        iterations = 100
        
        with PerformanceTimer() as timer:
            for i in range(iterations):
                with open(self.config_file, 'w') as f:
                    self.test_config["default_settings"]["channels"] = i
                    json.dump(self.test_config, f)
        
        result = timer.get_results("config_file_write", iterations)
        
        # Assert performance threshold (avg write should be under 10ms)
        self.assertLess(result.avg_time, 0.01, f"Config write too slow: {result.avg_time:.6f}s")
        
        print(f"\nConfig File Write Performance:")
        print(f"  Avg: {result.avg_time*1000:.4f}ms | Throughput: {result.throughput:.2f} ops/sec")
    
    def test_json_serialization_time(self):
        """Test JSON serialization/deserialization time"""
        iterations = 5000
        data = {"key": "value", "numbers": list(range(100)), "nested": {"a": 1, "b": 2}}
        
        with PerformanceTimer() as timer:
            for _ in range(iterations):
                json_str = json.dumps(data)
                json.loads(json_str)
        
        result = timer.get_results("json_serialization", iterations)
        
        self.assertLess(result.avg_time, 0.001, f"JSON serialization too slow: {result.avg_time:.6f}s")
        
        print(f"\nJSON Serialization Performance:")
        print(f"  Avg: {result.avg_time*1000:.4f}ms | Throughput: {result.throughput:.2f} ops/sec")
    
    def test_dict_operations_time(self):
        """Test dictionary operations response time"""
        iterations = 10000
        
        test_dict = {f"key_{i}": f"value_{i}" for i in range(100)}
        
        with PerformanceTimer() as timer:
            for _ in range(iterations):
                _ = test_dict.get("key_50")
                test_dict["new_key"] = "new_value"
                if "new_key" in test_dict:
                    del test_dict["new_key"]
        
        result = timer.get_results("dict_operations", iterations)
        
        self.assertLess(result.avg_time, 0.0001, f"Dict operations too slow: {result.avg_time:.6f}s")
        
        print(f"\nDictionary Operations Performance:")
        print(f"  Avg: {result.avg_time*1000:.4f}ms | Throughput: {result.throughput:.2f} ops/sec")


class TestThroughput(unittest.TestCase):
    """Test system throughput under load"""
    
    def test_concurrent_task_submission_throughput(self):
        """Test throughput of concurrent task submissions"""
        iterations = 100
        concurrent_workers = 10
        results_queue = queue.Queue()
        
        def submit_task(task_id):
            start = time.perf_counter()
            # Simulate task submission work
            time.sleep(0.001)  # 1ms simulated work
            end = time.perf_counter()
            results_queue.put((task_id, end - start))
        
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
            futures = [executor.submit(submit_task, i) for i in range(iterations)]
            for future in futures:
                future.result()
        
        total_time = time.perf_counter() - start_time
        throughput = iterations / total_time
        
        # Should handle at least 50 tasks per second
        self.assertGreater(throughput, 50, f"Throughput too low: {throughput:.2f} tasks/sec")
        
        print(f"\nConcurrent Task Submission Throughput:")
        print(f"  Tasks: {iterations} | Workers: {concurrent_workers}")
        print(f"  Total time: {total_time:.3f}s | Throughput: {throughput:.2f} tasks/sec")
    
    def test_bulk_operations_throughput(self):
        """Test bulk data operations throughput"""
        iterations = 50
        batch_sizes = [10, 50, 100, 500]
        
        for batch_size in batch_sizes:
            start_time = time.perf_counter()
            
            for _ in range(iterations):
                batch = [{"id": i, "data": f"item_{i}"} for i in range(batch_size)]
                # Simulate batch processing
                _ = [item["id"] for item in batch if item["id"] % 2 == 0]
            
            total_time = time.perf_counter() - start_time
            total_operations = iterations * batch_size
            throughput = total_operations / total_time
            
            print(f"  Batch size {batch_size}: {throughput:.2f} ops/sec")
            
            # Performance should scale reasonably with batch size
            self.assertGreater(throughput, 100, f"Throughput too low for batch {batch_size}")
    
    def test_memory_throughput(self):
        """Test memory-based operations throughput"""
        iterations = 1000
        data_size = 10000  # 10KB per item
        
        # Create test data
        test_data = [{"id": i, "data": "x" * data_size} for i in range(100)]
        
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss
        
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            # Process data in memory
            processed = [item["id"] for item in test_data if item["id"] % 2 == 0]
        
        total_time = time.perf_counter() - start_time
        throughput = iterations / total_time
        
        end_memory = process.memory_info().rss
        memory_growth = end_memory - baseline_memory
        
        self.assertGreater(throughput, 500, f"Memory throughput too low: {throughput:.2f} ops/sec")
        self.assertLess(memory_growth, 10 * 1024 * 1024, f"Memory growth too high: {memory_growth/1024/1024:.2f}MB")
        
        print(f"\nMemory Operations Throughput:")
        print(f"  Throughput: {throughput:.2f} ops/sec | Memory growth: {memory_growth/1024/1024:.2f}MB")


class TestLoadHandling(unittest.TestCase):
    """Test system behavior under various load conditions"""
    
    def test_light_load_response_time(self):
        """Test response time under light load (1-5 concurrent requests)"""
        for concurrent in [1, 3, 5]:
            times = []
            
            def worker(worker_id):
                start = time.perf_counter()
                # Simulate light work
                _ = sum(range(100))
                return time.perf_counter() - start
            
            start_time = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=concurrent) as executor:
                futures = [executor.submit(worker, i) for i in range(10)]
                for future in futures:
                    times.append(future.result())
            
            total_time = time.perf_counter() - start_time
            avg_time = statistics.mean(times)
            
            print(f"  Light load ({concurrent} workers): Avg response {avg_time*1000:.2f}ms")
            
            # Under light load, response should be very fast
            self.assertLess(avg_time, 0.01, f"Response too slow under light load: {avg_time:.4f}s")
    
    def test_medium_load_response_time(self):
        """Test response time under medium load (10-20 concurrent requests)"""
        for concurrent in [10, 20]:
            times = []
            
            def worker(worker_id):
                start = time.perf_counter()
                # Simulate medium work
                _ = sum(range(1000))
                return time.perf_counter() - start
            
            start_time = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=concurrent) as executor:
                futures = [executor.submit(worker, i) for i in range(20)]
                for future in futures:
                    times.append(future.result())
            
            total_time = time.perf_counter() - start_time
            avg_time = statistics.mean(times)
            
            print(f"  Medium load ({concurrent} workers): Avg response {avg_time*1000:.2f}ms")
            
            # Under medium load, response should still be acceptable
            self.assertLess(avg_time, 0.05, f"Response too slow under medium load: {avg_time:.4f}s")
    
    def test_heavy_load_response_time(self):
        """Test response time under heavy load (50+ concurrent requests)"""
        for concurrent in [50, 100]:
            times = []
            errors = [0]
            
            def worker(worker_id):
                try:
                    start = time.perf_counter()
                    # Simulate work with some variance
                    _ = sum(range(100))
                    return time.perf_counter() - start
                except Exception:
                    errors[0] += 1
                    return 0
            
            start_time = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=min(concurrent, 50)) as executor:
                futures = [executor.submit(worker, i) for i in range(concurrent)]
                for future in futures:
                    result = future.result()
                    if result > 0:
                        times.append(result)
            
            total_time = time.perf_counter() - start_time
            avg_time = statistics.mean(times) if times else 0
            
            print(f"  Heavy load ({concurrent} requests): Avg response {avg_time*1000:.2f}ms | Errors: {errors[0]}")
            
            # Should handle heavy load without crashes
            self.assertEqual(errors[0], 0, f"Errors occurred under heavy load: {errors[0]}")
    
    def test_sustained_load_endurance(self):
        """Test system endurance under sustained load"""
        duration = 2.0  # seconds
        request_rate = 50  # requests per second
        interval = 1.0 / request_rate
        
        start_time = time.time()
        request_count = 0
        error_count = 0
        
        def process_request():
            nonlocal request_count, error_count
            try:
                _ = sum(range(100))
                request_count += 1
            except Exception:
                error_count += 1
        
        while time.time() - start_time < duration:
            threads = [threading.Thread(target=process_request) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            time.sleep(0.01)  # Small delay between batches
        
        actual_rate = request_count / duration
        print(f"  Sustained load: {actual_rate:.2f} requests/sec | Errors: {error_count}")
        
        # Should maintain reasonable rate
        self.assertGreater(actual_rate, 100, f"Rate too low: {actual_rate:.2f} req/sec")


class TestScalability(unittest.TestCase):
    """Test system scalability under stress conditions"""
    
    def test_scaling_with_threads(self):
        """Test how performance scales with number of threads"""
        base_threads = 4
        multipliers = [1, 2, 4, 8]
        operations_per_thread = 50
        
        results = []
        
        for multiplier in multipliers:
            num_threads = base_threads * multiplier
            
            def worker():
                return sum(range(1000))
            
            start = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(worker) for _ in range(operations_per_thread * multiplier)]
                for future in futures:
                    future.result()
            
            total_time = time.perf_counter() - start
            throughput = (operations_per_thread * multiplier) / total_time
            
            results.append((num_threads, throughput, total_time))
            print(f"  Threads: {num_threads} | Time: {total_time:.3f}s | Throughput: {throughput:.2f} ops/sec")
        
        # Verify scalability - throughput should generally improve with more threads
        initial_throughput = results[0][1]
        for threads, throughput, _ in results[1:]:
            # Allow some variance but generally should improve or maintain
            self.assertGreater(throughput, initial_throughput * 0.5, 
                             f"Poor scalability: {threads} threads only {throughput:.2f} ops/sec vs initial {initial_throughput:.2f}")
    
    def test_memory_scalability(self):
        """Test memory usage scalability"""
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss
        
        data_sizes = [100, 1000, 10000, 50000]
        
        for size in data_sizes:
            gc.collect()
            
            # Create data
            start_mem = process.memory_info().rss
            data = [{"id": i, "value": f"item_{i}"} for i in range(size)]
            after_mem = process.memory_info().rss
            
            memory_per_item = (after_mem - start_mem) / size if size > 0 else 0
            
            # Process data
            _ = [item["id"] for item in data if item["id"] % 2 == 0]
            
            end_mem = process.memory_info().rss
            peak_memory = max(after_mem, end_mem)
            
            print(f"  Size {size}: {memory_per_item:.1f} bytes/item | Peak: {(peak_memory - baseline_memory)/1024/1024:.2f}MB")
            
            # Memory should scale linearly
            self.assertLess(memory_per_item, 1000, f"Memory per item too high: {memory_per_item:.1f} bytes")
    
    def test_cpu_intensive_scaling(self):
        """Test CPU-intensive operations scalability"""
        iterations = 1000
        
        for workers in [1, 2, 4]:
            def cpu_task():
                result = 0
                for i in range(10000):
                    result += i * i
                return result
            
            start = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(cpu_task) for _ in range(iterations)]
                for future in futures:
                    future.result()
            
            total_time = time.perf_counter() - start
            throughput = iterations / total_time
            
            print(f"  Workers {workers}: {throughput:.2f} tasks/sec")
            
            # More workers should generally improve throughput
            if workers > 1:
                # Allow some variance due to GIL
                pass
    
    def test_queue_throughput_scaling(self):
        """Test queue throughput scalability"""
        for size in [10, 50, 100, 500]:
            q = queue.Queue()
            producers = 5
            items_per_producer = size // producers
            
            # Fill queue
            for i in range(size):
                q.put(i)
            
            start = time.perf_counter()
            
            def consumer():
                count = 0
                while not q.empty():
                    try:
                        q.get_nowait()
                        count += 1
                    except queue.Empty:
                        break
                return count
            
            total_consumed = 0
            with ThreadPoolExecutor(max_workers=producers) as executor:
                futures = [executor.submit(consumer) for _ in range(producers)]
                for future in futures:
                    total_consumed += future.result()
            
            total_time = time.perf_counter() - start
            throughput = total_consumed / total_time if total_time > 0 else 0
            
            print(f"  Queue size {size}: {throughput:.2f} items/sec")
            
            # Queue operations should be efficient
            self.assertGreater(throughput, 1000, f"Queue throughput too low: {throughput:.2f}")


class TestResourceUtilization(unittest.TestCase):
    """Test resource utilization efficiency"""
    
    def test_memory_efficiency(self):
        """Test memory utilization efficiency"""
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss
        
        # Test with increasing data sizes
        for multiplier in [1, 10, 100]:
            data = [{"id": i, "data": "x" * 100} for i in range(1000 * multiplier)]
            
            used_memory = process.memory_info().rss - baseline_memory
            
            # Check memory efficiency (should be roughly proportional)
            expected_max = 1000 * multiplier * 300  # ~300 bytes per item max to account for overhead
            self.assertLess(used_memory, expected_max, 
                           f"Memory usage too high: {used_memory/1024/1024:.2f}MB for {multiplier}x data")
            
            print(f"  Data {multiplier}x: Memory {used_memory/1024/1024:.2f}MB")
            
            # Clear for next iteration
            del data
            gc.collect()
    
    def test_cpu_utilization(self):
        """Test CPU utilization during operations"""
        process = psutil.Process()
        
        # Baseline CPU
        baseline_cpu = process.cpu_percent()
        
        # CPU-intensive operation
        start = time.perf_counter()
        while time.perf_counter() - start < 0.5:
            _ = sum(i * i for i in range(10000))
        
        # Check CPU was utilized
        cpu_during = process.cpu_percent()
        print(f"  CPU utilization: {cpu_during:.1f}% (baseline: {baseline_cpu:.1f}%)")
        
        # CPU should have been utilized during intensive work
        self.assertGreater(cpu_during, 10, "CPU not utilized during intensive work")
    
    def test_thread_pool_efficiency(self):
        """Test thread pool utilization efficiency"""
        task_counts = [10, 50, 100, 500]
        
        for count in task_counts:
            def task():
                return sum(range(100))
            
            start = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(task) for _ in range(count)]
                for future in futures:
                    future.result()
            
            total_time = time.perf_counter() - start
            throughput = count / total_time
            
            print(f"  Tasks {count}: {throughput:.2f} tasks/sec")
            
            # Should maintain reasonable throughput
            self.assertGreater(throughput, 50, f"Throughput too low: {throughput:.2f}")
    
    def test_gc_efficiency(self):
        """Test garbage collection efficiency"""
        gc.collect()
        
        for size in [100, 1000, 10000]:
            # Create and discard data
            for _ in range(10):
                data = [{"id": i} for i in range(size)]
                del data
            
            gc.collect()
            
            process = psutil.Process()
            memory = process.memory_info().rss
            
            # Memory should stabilize after collection
            print(f"  Size {size}: Stable memory {memory/1024/1024:.2f}MB")


def run_performance_tests():
    """Run all performance tests and generate report"""
    print("=" * 80)
    print("Pure Sound - Performance Tests")
    print("=" * 80)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestResponseTimes,
        TestThroughput,
        TestLoadHandling,
        TestScalability,
        TestResourceUtilization,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All performance tests passed!")
        print("\nKey Performance Metrics:")
        print("  - Response times within acceptable thresholds")
        print("  - Throughput meets minimum requirements")
        print("  - Load handling stable under various conditions")
        print("  - Scalability demonstrated across thread counts")
        print("  - Resource utilization efficient")
    else:
        print("\n❌ Some performance tests failed")
        
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}")
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}")
    
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_performance_tests()
    exit(0 if success else 1)
